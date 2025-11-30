import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import os
import json

# setup
SAVE_FILE = "save.json"

FACES = {
    "idle": "(ᵔᴥᵔ)",
    "feed": "(￣﹃￣)",
    "play": "(ᐛ)", 
    "sleep": "(－_－) zzZ",
    "pet": "(˶ᵔ▽ᵔ˶)",
    "insult": "(ಥ﹏ಥ)",
    "dead": "(x_x)"
}

# pet class
class Tamagotchi:
    def __init__(self, name):
        self.name = name
        self.hunger = 100
        self.happiness = 100
        self.energy = 100
        self.age_seconds = 0
        self.alive = True
        self.last_update = time.time()
        self.current_action = "idle"

    def _clamp(self, v):
        return max(0, min(100, v))

    def adjust(self, field, amount):
        if not self.alive: return
        setattr(self, field, self._clamp(getattr(self, field) + amount))
        self.check_status()

    def check_status(self):
        if self.hunger <= 0 or self.energy <= 0:
            self.alive = False
            self.current_action = "dead"

    def mood(self):
        if not self.alive:
            return "dead"
        score = self.happiness + self.energy - self.hunger
        if 140 <= score <= 300: return "Happy"
        if 90 <= score <= 139:  return "Chillin"
        if 40 <= score <= 89:   return "Meh"
        return "Grumpy"

    def update(self):
        if not self.alive: return

        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        # decay logic
        decay_rate = dt * 0.5

        self.adjust("hunger", -decay_rate)
        self.adjust("energy", -decay_rate * 0.7)
        self.adjust("happiness", -decay_rate * 0.3)
        self.age_seconds += dt
        self.check_status()

    def to_dict(self):
        return {
            "name": self.name,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy,
            "age_seconds": self.age_seconds,
            "alive": self.alive,
            "last_update": self.last_update
        }

    @classmethod
    def from_dict(cls, data):
        pet = cls(data["name"])
        pet.hunger = data["hunger"]
        pet.happiness = data["happiness"]
        pet.energy = data["energy"]
        pet.age_seconds = data["age_seconds"]
        pet.alive = data["alive"]
        pet.last_update = time.time()
        return pet

# gui class
class TamaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tamagotchi")
        self.root.geometry("400x550")
        self.root.resizable(False, False)
        
        # load pet or crate new pet
        self.pet = self.load_game()
        if not self.pet:
            name = simpledialog.askstring("New Pet", "Name your creature:")
            if not name: name = "Egg"
            self.pet = Tamagotchi(name)

        # style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", thickness=20)
        
        # ui
        
        # top info
        self.frame_info = tk.Frame(root, pady=10)
        self.frame_info.pack(fill="x")
        
        self.lbl_name = tk.Label(self.frame_info, text=self.pet.name, font=("Arial", 16, "bold"))
        self.lbl_name.pack()
        
        self.lbl_mood = tk.Label(self.frame_info, text="Mood: Happy", font=("Arial", 10), fg="gray")
        self.lbl_mood.pack()

        # face
        self.lbl_face = tk.Label(root, text=FACES["idle"], font=("Courier New", 40, "bold"), pady=30)
        self.lbl_face.pack()

        # status message
        self.lbl_status = tk.Label(root, text="Your pet is waiting...", font=("Arial", 10, "italic"), fg="blue")
        self.lbl_status.pack(pady=(0, 20))

        # stats
        self.frame_stats = tk.Frame(root, padx=20)
        self.frame_stats.pack(fill="x")

        self.create_stat_bar("Hunger", "hunger_bar", "hunger_lbl")
        self.create_stat_bar("Happiness", "happy_bar", "happy_lbl")
        self.create_stat_bar("Energy", "energy_bar", "energy_lbl")

        # action Buttons
        self.frame_actions = tk.Frame(root, pady=20)
        self.frame_actions.pack()

        btn_opts = {'width': 8, 'padx': 5, 'pady': 5}
        
        tk.Button(self.frame_actions, text="Feed", command=self.action_feed, **btn_opts).grid(row=0, column=0)
        tk.Button(self.frame_actions, text="Play", command=self.action_play, **btn_opts).grid(row=0, column=1)
        tk.Button(self.frame_actions, text="Sleep", command=self.action_sleep, **btn_opts).grid(row=0, column=2)
        tk.Button(self.frame_actions, text="Pet", command=self.action_pet, **btn_opts).grid(row=1, column=0)
        tk.Button(self.frame_actions, text="Insult", command=self.action_insult, **btn_opts).grid(row=1, column=1)
        tk.Button(self.frame_actions, text="Quit", command=self.save_and_quit, bg="#ffcccc", **btn_opts).grid(row=1, column=2)

        # footer
        self.lbl_age = tk.Label(root, text="Age: 0s", font=("Arial", 8), fg="gray")
        self.lbl_age.pack(side="bottom", pady=5)

        # start loop
        self.update_gui_loop()

    def create_stat_bar(self, label_text, bar_attr, lbl_attr):
        frame = tk.Frame(self.frame_stats, pady=2)
        frame.pack(fill="x")
        
        tk.Label(frame, text=label_text, width=10, anchor="w").pack(side="left")
        
        bar = ttk.Progressbar(frame, orient="horizontal", length=200, mode="determinate", maximum=100)
        bar.pack(side="left", padx=5)
        setattr(self, bar_attr, bar)
        
        val_lbl = tk.Label(frame, text="100", width=4)
        val_lbl.pack(side="left")
        setattr(self, lbl_attr, val_lbl)

    # actions
    def set_action(self, action, message):
        if not self.pet.alive: return
        self.pet.current_action = action
        self.lbl_status.config(text=message)
        self.update_face()
        self.root.after(1000, self.reset_action)

    def reset_action(self):
        if self.pet.alive:
            self.pet.current_action = "idle"
            self.lbl_status.config(text="...")
            self.update_face()

    def action_feed(self):
        self.pet.adjust("hunger", 20)
        self.set_action("feed", f"{self.pet.name} munches on food.")

    def action_play(self):
        self.pet.adjust("happiness", 20)
        self.pet.adjust("energy", -10)
        self.set_action("play", f"You played with {self.pet.name}!")

    def action_sleep(self):
        self.pet.adjust("energy", 30)
        self.pet.adjust("hunger", -10)
        self.set_action("sleep", f"{self.pet.name} takes a quick nap.")

    def action_pet(self):
        self.pet.adjust("happiness", 10)
        self.set_action("pet", f"{self.pet.name} purrs.")

    def action_insult(self):
        self.pet.adjust("happiness", -20)
        self.set_action("insult", f"{self.pet.name} is offended!")

    # main loops
    def update_gui_loop(self):
        self.pet.update()
        
        # update bars
        self.hunger_bar['value'] = self.pet.hunger
        self.hunger_lbl['text'] = int(self.pet.hunger)
        
        self.happy_bar['value'] = self.pet.happiness
        self.happy_lbl['text'] = int(self.pet.happiness)
        
        self.energy_bar['value'] = self.pet.energy
        self.energy_lbl['text'] = int(self.pet.energy)

        # update text
        self.lbl_age.config(text=f"Age: {int(self.pet.age_seconds)}s")
        self.lbl_mood.config(text=f"Mood: {self.pet.mood()}")

        # check aliveness
        if not self.pet.alive:
            self.pet.current_action = "dead"
            self.lbl_status.config(text=f"{self.pet.name} has passed away...", fg="red")
            self.update_face()
        else:
            self.update_face()
            self.root.after(100, self.update_gui_loop)

    def update_face(self):
        # determine action and choose face
        face = FACES.get(self.pet.current_action, FACES["idle"])
        if not self.pet.alive:
            face = FACES["dead"]
        self.lbl_face.config(text=face)

    # save/load
    def save_and_quit(self):
        self.save_game()
        self.root.destroy()

    def save_game(self):
        with open(SAVE_FILE, "w") as f:
            json.dump(self.pet.to_dict(), f)

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            return None
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            return Tamagotchi.from_dict(data)
        except:
            return None

if __name__ == "__main__":
    root = tk.Tk()
    app = TamaGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.save_and_quit)
    root.mainloop()