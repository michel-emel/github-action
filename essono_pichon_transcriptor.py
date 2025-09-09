#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ewondo Transcriptor: Essono (2012) to Pichon (1950)
==================================================

API script for transcribing Ewondo text with detailed rule tracking.
"""

from typing import Dict, List
import unicodedata
import sys
import json


class EwondoTranscriptor:
    """
    Transcriptor for Ewondo language from Essono system to Pichon system.
    Tracks all applied rules for detailed output.
    """
    
    def __init__(self):
        """Initialize correspondence tables and rules."""
        # Consonant mappings
        self.consonant_map = {
            'ŋ': 'ṅ',  # Only consonant that changes (caron → dot above)
        }
        
        # Vowel mappings (character by character)
        self.vowel_map = {
            'ə': 'ë',  # schwa → e with diaeresis
            'ɛ': 'è',  # epsilon → e with grave accent
            'ɔ': 'ò',  # open o → o with grave accent
        }
        
        # Tonal diacritics to remove
        self.tonal_diacritics = [
            '\u0300',  # ◌̀ low tone
            '\u0301',  # ◌́ high tone  
            '\u0304',  # ◌̄ mid tone
            '\u030C',  # ◌̌ rising tone
            '\u0302',  # ◌̂ falling tone
        ]
    
    def analyze_word(self, word: str) -> Dict:
        """
        Analyze and transcribe a single word with rule tracking.
        """
        if not word.strip():
            return {
                'essono': word,
                'pichon': word,
                'rules': []
            }
        
        applied_rules = []
        current_word = word.strip()
        
        # Step 1: Convert consonants
        step1_word = current_word
        for essono_char, pichon_char in self.consonant_map.items():
            if essono_char in step1_word:
                step1_word = step1_word.replace(essono_char, pichon_char)
                applied_rules.append(f"Consonant: {essono_char} → {pichon_char}")
        
        # Step 2: Convert vowels (character by character)
        normalized_word = unicodedata.normalize('NFD', step1_word)
        step2_word = ""
        vowel_changes = set()
        for char in normalized_word:
            if char in self.vowel_map:
                converted_char = self.vowel_map[char]
                step2_word += converted_char
                vowel_changes.add(f"{char} → {converted_char}")
            else:
                step2_word += char
        
        for change in vowel_changes:
            applied_rules.append(f"Vowel: {change}")
        
        # Step 3: Remove tonal diacritics
        tones_removed = set()
        tone_names = {
            '\u0300': 'low tone (◌̀)',
            '\u0301': 'high tone (◌́)',
            '\u0304': 'mid tone (◌̄)',
            '\u030C': 'rising tone (◌̌)',
            '\u0302': 'falling tone (◌̂)'
        }
        
        step3_word = ""
        for char in step2_word:
            if char in self.tonal_diacritics:
                tones_removed.add(tone_names.get(char, 'tone'))
            else:
                step3_word += char
        
        step3_word = unicodedata.normalize('NFC', step3_word)
        
        if tones_removed:
            applied_rules.append(f"Removed tones: {', '.join(sorted(tones_removed))}")
        
        if not applied_rules:
            applied_rules.append("No changes needed")
        
        return {
            'essono': word.strip(),
            'pichon': step3_word,
            'rules': applied_rules
        }
    
    def transcribe_multiple(self, input_text: str) -> List[Dict]:
        """
        Transcribe multiple words separated by commas.
        """
        words = [word.strip() for word in input_text.split(',') if word.strip()]
        results = [self.analyze_word(word) for word in words]
        return results


def main():
    """
    Main function for command line usage and interactive mode.
    """
    transcriptor = EwondoTranscriptor()
    
    if len(sys.argv) > 1:
        # Command line argument provided
        input_text = sys.argv[1]
        results = transcriptor.transcribe_multiple(input_text)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        # Interactive mode
        print("=== EWONDO TRANSCRIPTOR: ESSONO → PICHON ===")
        print("Enter words separated by commas, or 'quit' to exit\n")
        
        while True:
            user_input = input("Enter Essono word(s): ").strip()
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            elif user_input:
                results = transcriptor.transcribe_multiple(user_input)
                
                print("\n" + "="*60)
                print(f"{'ESSONO':<20} {'PICHON':<20} {'RULES APPLIED'}")
                print("="*60)
                
                for result in results:
                    rules_str = "; ".join(result['rules'])
                    print(f"{result['essono']:<20} {result['pichon']:<20} {rules_str}")
                
                print("="*60 + "\n")
            else:
                print("Please enter some text to transcribe.\n")


if __name__ == "__main__":
    main()






