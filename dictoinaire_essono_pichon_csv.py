import csv
from essono_pichon_transcriptor import EwondoTranscriptor  

def transcribe_csv(input_file, output_file):
    """
    Ajoute une colonne 'Ewondo (Pichon)' à partir de la colonne 'Ewondo'.
    """
    transcriptor = EwondoTranscriptor()
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            rows = list(reader)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)

            for row_num, row in enumerate(rows):
                if row_num == 0:
                    # En-tête → ajouter la colonne Pichon
                    row.append('Ewondo (Pichon)')
                    writer.writerow(row)
                    continue

                if len(row) >= 3:
                    francais, ewondo, part_of_speech = row

                    # Transcrire le mot Ewondo
                    ewondo_transcribed = (
                        transcriptor.analyze_word(ewondo)['pichon']
                        if ewondo else ""
                    )

                    # Nouvelle ligne avec colonne ajoutée
                    writer.writerow([francais, ewondo, part_of_speech, ewondo_transcribed])
                else:
                    writer.writerow(row)
        
        print(f"✅ Transcription terminée: {output_file}")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    input_filename = "letter_a.csv"
    output_filename = "transcribed_csv.csv"
    transcribe_csv(input_filename, output_filename)
