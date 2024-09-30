import pandas as pd
import logging

log_file_path = '../dataset_attacchi_info.txt'
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(message)s')

# Funzione per il conteggio dei campioni per classe nella colonna 'type_attack'
def count_samples(csv_file_path, chunk_size=200000, delimiter=';'):
    class_counts = {}
    total_samples = 0

    logging.info('Inizio del conteggio dei campioni per classe.')

    for chunk_number, chunk in enumerate(pd.read_csv(csv_file_path, delimiter=delimiter, chunksize=chunk_size)):
        # Conta i campioni per classe in questo chunk
        class_counts_chunk = chunk['type_attack'].value_counts().to_dict()

        # Aggiorna i conteggi totali
        for class_label, count in class_counts_chunk.items():
            class_counts[class_label] = class_counts.get(class_label, 0) + count

        total_samples += len(chunk)

    # Log dei conteggi finali
    logging.info("Totale campioni per classe:")
    for class_label, count in class_counts.items():
        percentage = (count / total_samples) * 100 if total_samples > 0 else 0
        logging.info(f"Classe '{class_label}': {count} campioni ({percentage:.2f}%)")
        print(f"Classe '{class_label}': {count} campioni ({percentage:.2f}%)")

    logging.info(f"Totale campioni: {total_samples}")
    print(f"Totale campioni: {total_samples}")

    return class_counts

# Funzione per creare un dataset bilanciato tra più classi
def create_balanced_dataset(csv_file_path, output_file_path, chunk_size=100000, delimiter=';'):
    # Prima, conta i campioni per classe
    class_counts = count_samples(csv_file_path, chunk_size, delimiter)

    # Determina il numero minimo di campioni tra tutte le classi
    min_samples = min(class_counts.values())
    logging.info(f"Numero minimo di campioni tra le classi per il bilanciamento: {min_samples}")

    class_written_counts = {class_label: 0 for class_label in class_counts.keys()}

    # Inizializza DataFrame vuoti per ogni classe per memorizzare i campioni da scrivere
    class_samples_to_write = {class_label: [] for class_label in class_counts.keys()}

    # Legge il CSV in chunk
    for chunk_number, chunk in enumerate(pd.read_csv(csv_file_path, delimiter=delimiter, chunksize=chunk_size)):
        # Per ogni classe, campiona il numero richiesto di campioni
        for class_label in class_counts.keys():
            class_chunk = chunk[chunk['type_attack'] == class_label]

            # Determina quanti campioni campionare da questo chunk per la classe
            samples_needed = min_samples - class_written_counts[class_label]
            if samples_needed > 0 and not class_chunk.empty:
                # Campiona il numero richiesto o tutti i campioni disponibili se meno
                num_samples_to_take = min(samples_needed, len(class_chunk))
                sampled_class_chunk = class_chunk.sample(n=num_samples_to_take)
                class_samples_to_write[class_label].append(sampled_class_chunk)
                class_written_counts[class_label] += num_samples_to_take

        # Controlla se abbiamo raccolto abbastanza campioni per tutte le classi
        if all(count >= min_samples for count in class_written_counts.values()):
            break

    # Combina i campioni da tutte le classi e mescola
    combined_dataset = pd.concat([pd.concat(chunks) for chunks in class_samples_to_write.values()]).sample(frac=1)

    # Scrive nel file CSV di output
    combined_dataset.to_csv(output_file_path, index=False, sep=delimiter)

    logging.info(f"Dataset bilanciato creato con {min_samples} campioni per classe.")
    logging.info(f"Dataset bilanciato salvato in: {output_file_path}")

    print(f"Dataset bilanciato creato con {min_samples} campioni per classe.")
    print(f"Dataset bilanciato salvato in: {output_file_path}")

def main():
    csv_file_path = '/media/alberto/DATA/Tesi/dataset_attacchi.csv'
    balanced_csv_file_path = '../dataset_attacchi_bilanciato.csv'

    print("Scegli un'opzione:")
    print("1. Contare i campioni per classe")
    print("2. Bilanciare il dataset")

    scelta = input("Inserisci il numero della tua scelta: ")

    if scelta == "1":
        count_samples(csv_file_path)
    elif scelta == "2":
        create_balanced_dataset(csv_file_path, balanced_csv_file_path)
    else:
        print("Scelta non valida. Riprova.")

if __name__ == "__main__":
    main()