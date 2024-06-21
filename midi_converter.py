import mido
import os
import json

def convert_midi_to_4key_format(midi_file_path):
    midi_file = mido.MidiFile(midi_file_path)
    key_positions = [0, 1, 2, 3]  # Possible positions for the 4 keys
    current_pos = 0  # Start at position 0
    previous_event = None
    note_events = {}
    active_notes = {}

    tempo = 500000

    for msg in midi_file.tracks[0]:
        if msg.type == 'set_tempo':
            tempo = msg.tempo
            break

    for i, track in enumerate(midi_file.tracks):
        absolute_time = 0
        note_events[f'track_{i}'] = []
        active_notes[f'track_{i}'] = {}
        for msg in track:
            absolute_time += msg.time
            time_in_seconds = mido.tick2second(absolute_time, midi_file.ticks_per_beat, tempo)
            if msg.type == 'note_on' and msg.velocity > 0:
                # Determine note position based on pitch change
                if previous_event is not None:
                    note_range = previous_event['note'][0] - msg.note
                    if note_range < 0:
                        current_pos = (current_pos + 1) % 4
                    elif note_range > 0:
                        current_pos = (current_pos - 1) % 4
                
                    if previous_event['click_time'] == time_in_seconds:
                        note_events[f'track_{i}'][-1]['key_index'].add(current_pos)
                        note_events[f'track_{i}'][-1]['note'].append(msg.note)
                    else:
                        note_event = {
                            'key_index': {current_pos},
                            'click_time': time_in_seconds,
                            'note': [msg.note],
                            'velocity': msg.velocity,
                            'channel': msg.channel
                        }
                        note_events[f'track_{i}'].append(note_event)
                        active_notes[f'track_{i}'][msg.note] = note_event
                else:
                    note_event = {
                            'key_index': {current_pos},
                            'click_time': time_in_seconds,
                            'note': [msg.note],
                            'velocity': msg.velocity,
                            'channel': msg.channel
                        }
                    note_events[f'track_{i}'].append(note_event)
                    active_notes[f'track_{i}'][msg.note] = note_event
                previous_event = note_event

    return note_events

def convert_directory_to_json(source_directory, destination_base):
    for filename in os.listdir(source_directory):
        if filename.endswith('.mid') or filename.endswith('.midi'):
            midi_file_path = os.path.join(source_directory, filename)
            track_data = convert_midi_to_4key_format(midi_file_path)
            base_title = os.path.splitext(filename)[0]
            destination_directory = os.path.join(destination_base, base_title)

            # Create the destination directory if it doesn't exist
            os.makedirs(destination_directory, exist_ok=True)

            for track_name, note_events in track_data.items():
                for event in note_events:
                    event['key_index'] = list(event['key_index'])
                json_data = {
                    "audio": f"./songs/{base_title}/audio.wav",
                    "title": f"{base_title} [{track_name}]",
                    "background": f"./songs/{base_title}/bg.jpg",
                    "offset": 0.8,
                    "chart_data": note_events
                }
                json_filename = f"{track_name}.json"
                json_filepath = os.path.join(destination_directory, json_filename)
                with open(json_filepath, 'w') as json_file:
                    json.dump(json_data, json_file, indent=4)

if __name__ == '__main__':
    source_directory = 'to_convert'
    destination_base = './songs'
    convert_directory_to_json(source_directory, destination_base)
    print("Conversion Completed!")

