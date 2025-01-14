import pandas as pd
import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox
import os

def selecionar_arquivo_ou_pasta():
    resposta = messagebox.askquestion("Seleção", "Deseja selecionar um arquivo ou uma pasta?", icon='question')
    if resposta == 'yes':
        caminho = filedialog.askopenfilename(title="Selecione o arquivo CSV", filetypes=[("CSV files", "*.csv")])
        if caminho:
            entrada_arquivo.delete(0, ctk.END)
            entrada_arquivo.insert(0, caminho)
    else:
        caminho = filedialog.askdirectory(title="Selecione a pasta com arquivos CSV")
        if caminho:
            entrada_arquivo.delete(0, ctk.END)
            entrada_arquivo.insert(0, caminho)

def categorize_labels(label):
    label = label.strip().lower()
    if label in ['análise', 'bug', 'melhoria', 'dúvida', 'requisito', 'entrega', 'dúvida técnica']:
        return 'Tipo', label
    elif label in ['interface', 'checklist dev', 'code review', 'app', 'ambiente', 'front-PCPR', 'front-cidadao', 'back-end']:
        return 'Subtipo', label
    elif label in ['bloqueante', 'grave', 'médio', 'pequeno']:
        return 'Gravidade', label
    elif label.startswith('sprint') or label.startswith('entrega') or label.startswith('gm'):
        return 'Sprint', label
    elif label.startswith('os'):
        return 'OS', label
    elif label in ['to do [celepar]', 'analise aprovada [celepar]', 'to do [indra]', 'qualidade implementação [celepar]', 'doing [indra]', 
                   'done [indra]', 'review qualidade [celepar]', 'backlog', 'homologação entrega [cliente]', 
                   'analise aprovada [celepar]', 'qualidade artefatos [celepar]', 'review análise [indra]', 'doing', 'done']:
        return 'Estado', label
    return None, label

def extrair_nome_sistema(nome_arquivo):
    partes = nome_arquivo.split('-')
    if len(partes) > 2 and partes[0] == 'gcgit':
        return partes[1]
    return 'Desconhecido'

def extrair_dados():
    caminhoArquivo = entrada_arquivo.get()
    caminhoSaida = entrada_saida.get()
    
    if not caminhoArquivo or not caminhoSaida:
        messagebox.showwarning("Aviso", "Por favor, selecione o arquivo ou a pasta e insira o nome do arquivo de saída.")
        return

    try:
        if os.path.isfile(caminhoArquivo):
            df_final = processar_arquivo(caminhoArquivo)
            nome_arquivo = os.path.basename(caminhoArquivo)
            sistema = extrair_nome_sistema(nome_arquivo)
            df_final['Sistema'] = sistema
        elif os.path.isdir(caminhoArquivo):
            arquivos_csv = [f for f in os.listdir(caminhoArquivo) if f.endswith('.csv')]
            dataframes = []
            for arquivo in arquivos_csv:
                caminho_completo = os.path.join(caminhoArquivo, arquivo)
                df = processar_arquivo(caminho_completo)
                sistema = extrair_nome_sistema(arquivo)
                df['Sistema'] = sistema
                df = df[[col for col in df.columns if col != 'Sistema'] + ['Sistema']]
                dataframes.append(df)
            df_final = pd.concat(dataframes, ignore_index=True)
        else:
            messagebox.showerror("Erro", "Caminho inválido.")
            return

        df_final.to_csv(f"{caminhoSaida}.csv", index=False)
        messagebox.showinfo("Sucesso", "Arquivos processados e salvos com sucesso!")

        selecionar_colunas(df_final, caminhoSaida)

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

def processar_arquivo(caminhoArquivo):
    df = pd.read_csv(caminhoArquivo)
    df['Tipo'] = ''
    df['Subtipo'] = ''
    df['Gravidade'] = ''
    df['Sprint'] = ''
    df['OS'] = ''
    df['Estado'] = ''

    for i, row in df.iterrows():
        if pd.notna(row['Labels']):
            labels = row['Labels'].split(',')
            for label in labels:
                category, cleaned_label = categorize_labels(label)
                if category:
                    if df.at[i, category]:
                        df.at[i, category] += f', {cleaned_label}'
                    else:
                        df.at[i, category] = cleaned_label
    return df

def selecionar_colunas(df, caminho_saida):
    def salvar_arquivo():
        colunas_selecionadas = [col for col, var in colunas_vars.items() if var.get() == 1]
        df_modificado = df.drop(columns=colunas_selecionadas)

        novo_nome = f"{caminho_saida}_colunas_excluidas.csv"
        df_modificado.to_csv(novo_nome, index=False)
        messagebox.showinfo("Sucesso", f"Arquivo salvo como: {novo_nome}")
        janela_colunas.destroy()

    janela_colunas = ctk.CTkToplevel(janela)
    janela_colunas.title("Seleção de Colunas")
    janela_colunas.geometry("400x1600")

    label_instrucao = ctk.CTkLabel(janela_colunas, text="Selecione as colunas que deseja excluir:")
    label_instrucao.pack(pady=10)

    colunas_vars = {}
    for coluna in df.columns:
        var = ctk.IntVar()
        checkbox = ctk.CTkCheckBox(janela_colunas, text=coluna, variable=var)
        checkbox.pack(anchor="w")
        colunas_vars[coluna] = var

    botao_salvar = ctk.CTkButton(janela_colunas, text="Salvar", command=salvar_arquivo)
    botao_salvar.pack(pady=20)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

janela = ctk.CTk()
janela.title("Extração de Dados")
janela.geometry("400x300")

label_arquivo = ctk.CTkLabel(janela, text="Arquivo ou Pasta CSV:")
label_arquivo.pack(pady=10)

entrada_arquivo = ctk.CTkEntry(janela, width=300)
entrada_arquivo.pack()

botao_selecionar = ctk.CTkButton(janela, text="Selecionar Arquivo ou Pasta", command=selecionar_arquivo_ou_pasta)
botao_selecionar.pack(pady=10)

label_saida = ctk.CTkLabel(janela, text="Nome do Arquivo de Saída (sem .csv):")
label_saida.pack(pady=10)

entrada_saida = ctk.CTkEntry(janela, width=300)
entrada_saida.pack()

botao_extrair = ctk.CTkButton(janela, text="EXTRAIR", command=extrair_dados)
botao_extrair.pack(pady=20)

janela.mainloop()
