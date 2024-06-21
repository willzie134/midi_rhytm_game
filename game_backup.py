from ursina import *
from midi_converter import *

app = Ursina()
camera.orthographic = True
camera.fov = 8

class ScoreScreen:
    def __init__(self):
        self.score = 0
        self.hit = 0
        self.miss = 0
        self.max_combo = 0
        self.background = Entity(model='quad', color=color.black, scale=(14.2, 8), position=(0, 0, 1), enabled=False)
        self.win_text = Text(text='You win!', color=color.red, scale=3, position=(0, 0.4, -.2), enabled=False)
        self.hit_text = Text(text=f'Hit  : {self.hit}', color=color.white, scale=2, position=(0, 0.3, -.2), enabled=False)
        self.miss_text = Text(text=f'Score: {self.miss}', color=color.white, scale=2, position=(0, 0.2, -.2), enabled=False)
        self.max_combo_text = Text(text=f'Score: {self.max_combo}', color=color.white, scale=2, position=(0, 0.1, -.2), enabled=False)
        self.score_text = Text(text=f'Score: {self.score}', color=color.white, scale=2, position=(0, 0, -.2), enabled=False)
        self.quit_text = Text(text='Press Q to quit', color=color.white, scale=1.5, position=(0, -0.1, -.2), enabled=False)

    def input(self, key):
        if key == 'q':
            quit()

    def update(self):
        pass

    def hide(self):
        self.background.enabled = False
        self.win_text.enabled = False
        self.score_text.enabled = False
        self.quit_text.enabled = False
        self.hit_text.enabled = False
        self.miss_text.enabled = False
        self.max_combo_text.enabled = False

    def show(self, score, hit, miss, max_combo, win=True):
        global update, input
        update = self.update
        input = self.input


        self.background.enabled = True
        self.win_text.enabled = True
        self.score_text.enabled = True
        self.hit_text.enabled = True
        self.miss_text.enabled = True
        self.max_combo_text.enabled = True
        self.quit_text.enabled = True
        self.hit_text.text = f'Hit: {hit}'
        self.miss_text.text = f'Miss: {miss}'
        self.max_combo_text.text = f'Max Combo: {max_combo}'
        self.score_text.text = f'Score: {score}'

        if not win:
            self.win_text.text = 'You Lose~'    
        else:
            self.win_text.text = 'You Win!'    

class Gameplay:
    def __init__(self, song_data):
        self.hit = 0
        self.miss = 0
        self.combo = 0
        self.max_combo = 0
        self.score = 0
        self.hp = 100
        self.damage = 10
        self.max_hp = 100
        self.audio_played = False
        self.DURATION = 1.0
        self.LOWER_BOUND = -3.2
        self.UPPER_BOUND = -2.0

        self.song_data = song_data
        self.chart_data = self.song_data['chart_data']
        self.entities = []
        
        self.background = Entity(model='quad', texture=song_data['background'], scale=(14.2, 8, 2.0), position=(0, 0, 1))
        self.play_area = Entity(model='quad', color=color.black90, scale=(4.2, 8.0), position=(-4.5, 0.0))
        self.hitbox_area = Entity(model='quad', color=color.white, scale=(4.2, .2), position=(-4.5, -3.0))
        self.hp_bar = Entity(model='quad', color=color.white, scale=(.4, 5.2), position=(-2.2, -1.5, -.5))
        self.hp_indicator = Entity(model='quad', color=color.black, scale=(.25, 5.0), position=(-2.2, -1.5, -.8))
        self.total_time = 0

        self.key_press_entities = [
            Entity(model='quad', color=color.white, scale=(1.0, 0.1), position=(-6.0, -3.0, -.2)),
            Entity(model='quad', color=color.white, scale=(1.0, 0.1), position=(-5.0, -3.0, -.2)),
            Entity(model='quad', color=color.white, scale=(1.0, 0.1), position=(-4.0, -3.0, -.2)),
            Entity(model='quad', color=color.white, scale=(1.0, 0.1), position=(-3.0, -3.0, -.2))
        ]

        self.key_entities = [
            {'color': color.red, 'pos': (-6.0, 4.0)},
            {'color': color.green, 'pos': (-5.0, 4.0)},
            {'color': color.blue, 'pos': (-4.0, 4.0)},
            {'color': color.yellow, 'pos': (-3.0, 4.0)},
        ]
        
        self.keys = []

        self.combo_text = Text(text=f'{self.combo}', position=(-0.575, 0.45), color=color.white, scale=1.5)
        self.score_text = Text(text=f'{self.score}', position=(0.4, 0.48), color=color.white, scale=1.5)
        # max_combo_text = Text(text=f'Max Combo: {max_combo}', origin=(-1.0, -1.0), color=color.white, scale=1)

        self.entities.extend([
            self.background, self.play_area, self.hitbox_area, self.hp_bar, self.hp_indicator, self.combo_text, self.score_text
        ])

        self.entities.extend(self.key_press_entities)

        self.audio = Audio(song_data['audio'], autoplay=False, loop=False)

    def show(self):
        global update, input
        update = self.update
        input = self.input
        for entity in self.entities:
            entity.enabled = True

    def hide(self):
        for entity in self.entities:
            entity.enabled = False
        for key in self.keys:
            key.enabled = False
        self.audio.stop()

    def update_hp_indicator(self):
        hp_ratio = self.hp / self.max_hp
        self.hp_indicator.scale_y = 5.0 * hp_ratio
        self.hp_indicator.position = (-2.2, -1.5 - (1 - hp_ratio) * 2.5, -.8)  # Adjust position to keep bottom aligned

    
    def remove_key(self, key, hit):

        if hit:
            self.combo += 1
            self.score += 100 + (self.combo * 10)
            self.hp = min(self.hp + 5, self.max_hp)
            self.max_combo = max(self.max_combo, self.combo)
        else:
            self.combo = 0
            self.hp -= self.damage
            if self.hp <= 0:
                self.hide()
                score_screen.show(self.score, self.hit, self.miss, self.max_combo, win=False)

        self.combo_text.text = f'{self.combo}X'
        self.score_text.text = f'{self.score}'
        self.update_hp_indicator()

        destroy(key)
        self.keys.remove(key)


    def generate_key(self, note):

        indices = note['key_index']
        for index in indices:
            key = Entity(model='quad', color=self.key_entities[index]['color'], scale=(.9, .2), position=self.key_entities[index]['pos'])
            key.start_position = key.position.y  # Store the starting position
            key.end_position = self.LOWER_BOUND  # Store the end position
            key.total_time = self.DURATION  # Total time to move
            key.elapsed_time = 0  # Time elapsed since start
            self.keys.append(key)


    def check_key_press(self, key_index):
        
        for key in self.keys:
            if key.y <= self.UPPER_BOUND and key.position[0] == self.key_entities[key_index]['pos'][0]:
                self.remove_key(key, True)
                self.key_press_entities[key_index].color = color.gold
                invoke(setattr,  self.key_press_entities[key_index], 'color', color.white, delay=0.1)
                return
            
        self.key_press_entities[key_index].color = color.black
        invoke(setattr,  self.key_press_entities[key_index], 'color', color.white, delay=0.1)

    def input(self, key):
        if key == 'a':
            self.check_key_press(0) 
            
        elif key == 's':
            self.check_key_press(1) 

        elif key == 'd':
            self.check_key_press(2) 
            
        elif key == 'f':
            self.check_key_press(3) 

    # Function to update animation every frame
    def update(self):

        if not self.audio_played and self.total_time > 3 + self.song_data['offset']: # Set the offset here
            self.audio.play()
            self.audio_played = True

        self.total_time += time.dt


        if len(self.chart_data) == 0 and len(self.keys) == 0:
            score_screen.show(self.score, self.hit, self.miss, self.max_combo)

        for note in self.chart_data:
            if self.total_time >= note['click_time'] + 3:
                self.generate_key(note)
                self.chart_data.remove(note)
            else:
                break

        for key in self.keys:
            key.elapsed_time += time.dt
            key.y = lerp(key.start_position, key.end_position, key.elapsed_time / key.total_time)
            # Check if key reaches hit area
            if key.y < self.LOWER_BOUND: 
                self.remove_key(key, False)

class SongSelection:
    def __init__(self):
        self.background = Entity(model='quad', texture='bg-aru.jpg', scale=(14.2, 8), position=(0, 0, 1))

        self.title = Text(text="Select a Song", position=(-.54, 0.4), scale=2, origin=(0, 0), color=color.white)

        self.background2 = Entity(model='quad', color=color.black90, scale=(6.0, 8.0), position=(-4.5, 0.0))
        
        self.songs = self.load_songs('songs')
        self.buttons = []

        for i, song in enumerate(self.songs):
            button = Button(text=song['title'], color=color.azure, scale=(0.7, 0.075), position=(-.54, 0.3 - i * 0.08))
            button.on_click = Func(self.select_song, song)
            self.buttons.append(button)

    def load_songs(self, directory):
        songs = []
        for song_dir in os.listdir(directory):
            song_path = os.path.join(directory, song_dir)
            if os.path.isdir(song_path):
                for file in os.listdir(song_path):
                    if file.endswith('.json'):
                        with open(os.path.join(song_path, file), 'r') as f:
                            song_data = json.load(f)
                            song_data['directory'] = song_path
                            song_data['filename'] = file
                            song_data['display_name'] = f"{song_data['title']} [{file.replace('.json', '')}]"
                            songs.append(song_data)
        return songs

    def select_song(self, song):
        print(f"Selected song: {song['display_name']}")
        self.start_gameplay(song)

    def input(self, _):
        pass

    def update(self):
        pass

    def show(self):
        global update, input
        update = self.update
        input = self.input

        for button in self.buttons:
            button.enable()
        self.title.enable()
        self.background.enable()
        self.background2.enable()
        

    def hide(self):
        for button in self.buttons:
            button.enabled = False
        self.title.enabled = False
        self.background.enabled = False
        self.background2.enabled = False

    def start_gameplay(self, song_data):
        self.hide()
        
        # Start the gameplay
        Gameplay(song_data).show()


song_selection = SongSelection()
score_screen = ScoreScreen()

if __name__ == '__main__':
    app.run()


# app = Ursina()

# camera.orthographic = True
# camera.fov = 8
# hit = 0
# miss = 0
# combo = 0
# score = 0
# hp = 100  # Initial HP
# max_hp = 100  # Maximum HP
# # max_combo = 0
# audio_played = False

# DURATION = 1.0
# LOWER_BOUND = -3.2 
# UPPER_BOUND = -2.0

# background = Entity(model='quad', texture='bg-aru.jpg', scale=(14.2, 8), position=(0, 0, 1))
# # background = Sky(texture='bg-aru.jpg')

# play_area = Entity(model='quad', color=color.black90, scale=(4.2, 8.0), position=(-4.5, 0.0))
# hitbox_area = Entity(model='quad', color=color.white, scale=(4.2, .2), position=(-4.5, -3.0))
# hp_bar = Entity(model='quad', color=color.white, scale=(.4, 5.2), position=(-2.2, -1.5, -.5))
# hp_indicator = Entity(model='quad', color=color.black, scale=(.25, 5.0), position=(-2.2, -1.5, -.8))
# total_time = 0

# key_press_entities = [
#     Entity(model='quad', color=color.white, scale=(1.0, 0.1), position=(-6.0, -3.0, -.2)),
#     Entity(model='quad', color=color.white, scale=(1.0, 0.1), position=(-5.0, -3.0, -.2)),
#     Entity(model='quad', color=color.white, scale=(1.0, 0.1), position=(-4.0, -3.0, -.2)),
#     Entity(model='quad', color=color.white, scale=(1.0, 0.1), position=(-3.0, -3.0, -.2))
# ]

# key_entities = [
#     {'color': color.red, 'pos': (-6.0, 4.0)},
#     {'color': color.green, 'pos': (-5.0, 4.0)},
#     {'color': color.blue, 'pos': (-4.0, 4.0)},
#     {'color': color.yellow, 'pos': (-3.0, 4.0)},
# ]

# chart_data = convert_midi_to_4key_format('Unwelcome_School.mid')['track 0']

# keys = []

# combo_text = Text(text=f'{combo}X', position=(0.6, -0.45), color=color.white, scale=1.5)
# score_text = Text(text=f'{score}', position=(0.6, 0.48), color=color.white, scale=1.5)
# # max_combo_text = Text(text=f'Max Combo: {max_combo}', origin=(-1.0, -1.0), color=color.white, scale=1)

# audio = Audio('Unwelcome_School.wav', autoplay=False, loop=False)

# def update_hp_indicator():
#     global hp
#     hp_ratio = hp / max_hp
#     hp_indicator.scale_y = 5.0 * hp_ratio
#     hp_indicator.position = (-2.2, -1.5 - (1 - hp_ratio) * 2.5, -.8)  # Adjust position to keep bottom aligned

# def remove_key(key, hit):
#     global combo, score, hp
#     # global combo, max_combo

#     if hit:
#         combo += 1
#         score += 100 + (combo * 10)
#         hp = min(hp + 5, max_hp)
#         # max_combo = max(max_combo, combo)
#     else:
#         combo = 0
#         hp -= 10
#         if hp <= 0:
#             print('Game Over')
#             application.quit()

#     combo_text.text = f'{combo}X'
#     score_text.text = f'{score}'
#     update_hp_indicator()

#     destroy(key)
#     keys.remove(key)


# def generate_key(note):

#     indices = note['key_index']
#     for index in indices:
#         key = Entity(model='quad', color=key_entities[index]['color'], scale=(.9, .2), position=key_entities[index]['pos'])
#         key.start_position = key.position.y  # Store the starting position
#         key.end_position = LOWER_BOUND  # Store the end position
#         key.total_time = DURATION  # Total time to move
#         key.elapsed_time = 0  # Time elapsed since start
#         keys.append(key)


# def check_key_press(key_index):
    
#     for key in keys:
#         if key.y <= UPPER_BOUND and key.position[0] == key_entities[key_index]['pos'][0]:
#             remove_key(key, True)
#             key_press_entities[key_index].color = color.gold
#             invoke(setattr,  key_press_entities[key_index], 'color', color.white, delay=0.1)
#             return
        
#     key_press_entities[key_index].color = color.black
#     invoke(setattr,  key_press_entities[key_index], 'color', color.white, delay=0.1)

# def set_key_press_color(delay, entity, color_value):
#     invoke(setattr, entity, 'color', color_value, delay=delay)

# def input(key):
#     if key == 'a':
#         check_key_press(0) 
        
#     elif key == 's':
#         check_key_press(1) 

#     elif key == 'd':
#         check_key_press(2) 
         
#     elif key == 'f':
#         check_key_press(3) 

# audio_played = False
# # Function to update animation every frame
# def update():
#     global total_time, audio_played

#     if not audio_played and total_time > 3 + .8: # Set the offset here
#         audio.play()
#         audio_played = True

#     total_time += time.dt

#     for note in chart_data:
#         if total_time >= note['click_time'] + 3:
#             generate_key(note)
#             chart_data.remove(note)
#         else:
#             break


#     for key in keys:
#         key.elapsed_time += time.dt
#         key.y = lerp(key.start_position, key.end_position, key.elapsed_time / key.total_time)
#         # Check if key reaches hit area
#         if key.y < -3.2: 
#             remove_key(key, False)



# app.run()