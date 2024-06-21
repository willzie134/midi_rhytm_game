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
            self.hide()
            song_selection.show()

    def update(self):
        pass

    def hide(self):
        self.background.disable()
        self.win_text.disable()
        self.score_text.disable()
        self.quit_text.disable()
        self.hit_text.disable()
        self.miss_text.disable()
        self.max_combo_text.disable()

    def show(self, score, hit, miss, max_combo, win=True):
        global update, input
        update = self.update
        input = self.input


        self.background.enable()
        self.win_text.enable()
        self.score_text.enable()
        self.hit_text.enable()
        self.miss_text.enable()
        self.max_combo_text.enable()
        self.quit_text.enable()
        self.hit_text.text = f'Hit: {hit}'
        self.miss_text.text = f'Miss: {miss}'
        self.max_combo_text.text = f'Max Combo: {max_combo}'
        self.score_text.text = f'Score: {score}'

        if not win:
            self.win_text.text = 'You Lose~'    
        else:
            self.win_text.text = 'You Win!'    

class Gameplay:
    def __init__(self):

        self.hit = 0
        self.miss = 0
        self.combo = 0
        self.max_combo = 0
        self.score = 0
        self.hp = 100
        self.damage = 10
        self.max_hp = 100
        self.DURATION = 1.0
        self.LOWER_BOUND = -3.2
        self.UPPER_BOUND = -2.0
        
        self.entities = []
        
        self.play_area = Entity(model='quad', color=color.black90, scale=(4.2, 8.0), position=(-4.5, 0.0), enabled=False)
        self.hitbox_area = Entity(model='quad', color=color.white, scale=(4.2, .2), position=(-4.5, -3.0), enabled=False)
        self.hp_bar = Entity(model='quad', color=color.white, scale=(.4, 5.2), position=(-2.2, -1.5, -.5), enabled=False)
        self.hp_indicator = Entity(model='quad', color=color.black, scale=(.25, 5.0), position=(-2.2, -1.5, -.8), enabled=False)

        self.key_press_entities = [
            Entity(model='quad', color=color.white, scale=(1.0, 0.1), position=(-6.0, -3.0, -.2), enabled=False),
            Entity(model='quad', color=color.white, scale=(1.0, 0.1), position=(-5.0, -3.0, -.2), enabled=False),
            Entity(model='quad', color=color.white, scale=(1.0, 0.1), position=(-4.0, -3.0, -.2), enabled=False),
            Entity(model='quad', color=color.white, scale=(1.0, 0.1), position=(-3.0, -3.0, -.2), enabled=False)
        ]

        self.key_entities = [
            {'color': color.red, 'pos': (-6.0, 4.0)},
            {'color': color.green, 'pos': (-5.0, 4.0)},
            {'color': color.blue, 'pos': (-4.0, 4.0)},
            {'color': color.yellow, 'pos': (-3.0, 4.0)},
        ]
        
        self.combo_text = Text(text=f'{self.combo}', position=(-0.575, 0.45), color=color.white, scale=1.5, enabled=False)
        self.score_text = Text(text=f'{self.score}', position=(0.4, 0.48), color=color.white, scale=1.5, enabled=False)
        # max_combo_text = Text(text=f'Max Combo: {max_combo}', origin=(-1.0, -1.0), color=color.white, scale=1)

        self.entities.extend([
            self.play_area, self.hitbox_area, self.hp_bar, self.hp_indicator, self.combo_text, self.score_text
        ])

        self.entities.extend(self.key_press_entities)

    def set_attrs(self, song_data):
        self.keys = []
        self.total_time = 0
        
        self.hit = 0
        self.miss = 0
        self.combo = 0
        self.max_combo = 0
        self.score = 0
        self.hp = 100
        self.max_hp = 100
        self.audio_played = False

        self.background = Entity(model='quad', texture=song_data['background'], scale=(14.2, 8, 2.0), position=(0, 0, 1))
        self.song_data = song_data
        self.chart_data = self.song_data['chart_data']
        self.audio = Audio(song_data['audio'], autoplay=False, loop=False)

        self.entities.append(self.background)

    def show(self, song_data):
        global update, input
        update = self.update
        input = self.input
        self.set_attrs(song_data)
        for entity in self.entities:
            entity.enable()

    def hide(self):
        for entity in self.entities:
            entity.disable()

        for key in self.keys:
            key.disable()
            
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
            self.hit += 1
        else:
            self.combo = 0
            self.hp -= self.damage
            self.miss += 1
            if self.hp <= 0:
                self.hide()
                score_screen.show(self.score, self.hit, self.miss, self.max_combo, win=False)

        self.combo_text.text = f'{self.combo}'
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
            self.hide()
            score_screen.show(self.score, self.hit, self.miss, self.max_combo)

        for note in self.song_data['chart_data']:
            # print(note['click_time'])
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
        self.background = Entity(model='quad', texture='bg crop.jpg', scale=(14.2, 8), position=(0, 0, 1))

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
            button.disable()
        self.title.disable()
        self.background.disable()
        self.background2.disable()

    def start_gameplay(self, song_data):
        self.hide()
        
        # Start the gameplay
        gameplay.show(song_data)



if __name__ == '__main__':
    song_selection = SongSelection()
    score_screen = ScoreScreen()
    gameplay = Gameplay()
    app.run()
