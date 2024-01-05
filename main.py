import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import csv


def summarize_staking_rewards(df, columns_order):
    staking_rewards = df[df['Operation'] == 'Staking reward'].copy()
    staking_rewards['Amount'] = pd.to_numeric(staking_rewards['Amount'], errors='coerce')
    staking_rewards['FIAT value'] = pd.to_numeric(staking_rewards['FIAT value'], errors='coerce')

    summary = staking_rewards.groupby(staking_rewards['Date'].dt.normalize()).agg({
        'Amount': 'sum',
        'FIAT value': 'sum',
        'Coin/Asset': 'first',
        'FIAT currency': 'first'
    }).reset_index()

    summary['Date'] = summary['Date'] + pd.Timedelta(hours=23, minutes=59)
    summary['Operation'] = 'Staking reward'
    add_missing_columns(df, summary, columns_order)

    # Korrigieren der Spaltenreihenfolge und Hinzufügen fehlender Spalten
    summary = summary.reindex(columns=columns_order)
    for column in columns_order:
        if column not in summary.columns:
            summary[column] = ''

    return summary

def summarize_entry_staking_wallet(df, columns_order):
    entry_staking_rewards = df[df['Operation'] == 'Entry staking wallet'].copy()
    entry_staking_rewards['Amount'] = pd.to_numeric(entry_staking_rewards['Amount'], errors='coerce')
    entry_staking_rewards['FIAT value'] = pd.to_numeric(entry_staking_rewards['FIAT value'], errors='coerce')

    summary = entry_staking_rewards.groupby(entry_staking_rewards['Date'].dt.normalize()).agg({
        'Amount': 'sum',
        'FIAT value': 'sum',
        'Coin/Asset': 'first',
        'FIAT currency': 'first'
    }).reset_index()

    summary['Date'] = summary['Date'] + pd.Timedelta(hours=23, minutes=59)
    summary['Operation'] = 'Entry staking wallet'

    # Korrigieren der Spaltenreihenfolge und Hinzufügen fehlender Spalten
    summary = summary.reindex(columns=columns_order)
    for column in columns_order:
        if column not in summary.columns:
            summary[column] = ''

    return summary

def summarize_liquidity_mining_rewards_btc_dfi(df, columns_order):
    liquidity_rewards = df[df['Operation'] == 'Liquidity mining reward BTC-DFI'].copy()
    liquidity_rewards['Amount'] = pd.to_numeric(liquidity_rewards['Amount'], errors='coerce')
    liquidity_rewards['FIAT value'] = pd.to_numeric(liquidity_rewards['FIAT value'], errors='coerce')

    liquidity_rewards['Date'] = pd.to_datetime(liquidity_rewards['Date']).dt.tz_localize(None).dt.normalize()

    summary = liquidity_rewards.groupby(['Date', 'Coin/Asset']).agg({
        'Amount': 'sum',
        'FIAT value': 'sum',
        'FIAT currency': 'first'
    }).reset_index()

    summary = summary[(summary['Amount'] != 0) | (summary['FIAT value'] != 0)]

    summary['Date'] = summary['Date'] + pd.Timedelta(hours=23, minutes=59)
    summary['Operation'] = 'Liquidity mining reward BTC-DFI'

    summary = summary.reindex(columns=columns_order)
    for column in columns_order:
        if column not in summary.columns:
            summary[column] = ''

    return summary

def summarize_liquidity_mining_rewards_eth_dfi(df, columns_order):
    liquidity_rewards = df[df['Operation'] == 'Liquidity mining reward ETH-DFI'].copy()
    liquidity_rewards['Amount'] = pd.to_numeric(liquidity_rewards['Amount'], errors='coerce')
    liquidity_rewards['FIAT value'] = pd.to_numeric(liquidity_rewards['FIAT value'], errors='coerce')

    liquidity_rewards['Date'] = pd.to_datetime(liquidity_rewards['Date']).dt.tz_localize(None).dt.normalize()

    summary = liquidity_rewards.groupby(['Date', 'Coin/Asset']).agg({
        'Amount': 'sum',
        'FIAT value': 'sum',
        'FIAT currency': 'first'
    }).reset_index()

    summary = summary[(summary['Amount'] != 0) | (summary['FIAT value'] != 0)]

    summary['Date'] = summary['Date'] + pd.Timedelta(hours=23, minutes=59)
    summary['Operation'] = 'Liquidity mining reward ETH-DFI'

    summary = summary.reindex(columns=columns_order)
    for column in columns_order:
        if column not in summary.columns:
            summary[column] = ''

    return summary

def summarize_daily(df, columns_order):
    staking_summary = summarize_staking_rewards(df, columns_order)
    liquidity_summary_btc_dfi = summarize_liquidity_mining_rewards_btc_dfi(df, columns_order)
    liquidity_summary_eth_dfi = summarize_liquidity_mining_rewards_eth_dfi(df, columns_order)
    entry_staking_summary = summarize_entry_staking_wallet(df, columns_order)

    # Zusammenführen der Zusammenfassungen
    summary = pd.concat([staking_summary, liquidity_summary_btc_dfi, liquidity_summary_eth_dfi, entry_staking_summary]).sort_values(by='Date')

    return summary

def add_missing_columns(df, summary, columns_order):
    # Fügen Sie fehlende Spalten mit Standardwerten hinzu
    for column in columns_order:
        if column not in summary.columns:
            summary[column] = '' if df[column].dtype == object else 0

    # Ordnen Sie die Spalten entsprechend der Reihenfolge in columns_order
    summary = summary[columns_order]
    return summary

def process_csv(input_file, output_file):
    df = pd.read_csv(input_file, parse_dates=['Date'])
    df['Date'] = pd.to_datetime(df['Date'], utc=True).dt.tz_localize(None)
    columns_order = df.columns.tolist()

    # Direkt summarize_daily aufrufen, da wir nur tägliche Zusammenfassungen verwenden
    summary = summarize_daily(df, columns_order)

    # Entfernen der Original-Einträge für "Staking reward", "Liquidity mining reward BTC-DFI" und "Entry staking wallet"
    filtered_df = df[
        ~df['Operation'].isin(['Staking reward', 'Liquidity mining reward BTC-DFI', 'Liquidity mining reward ETH-DFI', 'Entry staking wallet'])]

    result = pd.concat([summary, filtered_df]).sort_values(by='Date')

    # Öffnen der Ausgabedatei im Schreibmodus
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        # Schreiben des Headers ohne Anführungszeichen
        file.write(','.join(columns_order) + '\n')

        # Schreiben des Datenkörpers mit Anführungszeichen
        result.to_csv(file, index=False, header=False, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

    messagebox.showinfo("Erfolg", f"Datei erfolgreich gespeichert als\n{output_file}")
    root.destroy()

def select_input_file():
    input_file = filedialog.askopenfilename(title="Wählen Sie die Eingabedatei aus",
                                            filetypes=[("CSV Dateien", "*.csv")])
    if input_file:
        output_file = filedialog.asksaveasfilename(title="Speichern als",
                                                   defaultextension=".csv",
                                                   filetypes=[("CSV Dateien", "*.csv")])
        if output_file:
            process_csv(input_file, output_file)  # aktualisierter Aufruf ohne 'basis'


# GUI Initialisierung
root = tk.Tk()
root.withdraw()

# Dateiauswahl Dialog
select_input_file()

# Beenden des tkinter Loops
root.mainloop()
