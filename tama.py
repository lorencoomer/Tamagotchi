import time
import os
import json
import datetime

save_file = "save.json"

faces = {
    "idle": "(ᵔᴥᵔ)",
    "feed": "(￣﹃￣)  *burp*",
    "play": "(ᐛ)", 
    "sleep": "(－_－) zzZ",
    "pet": "(˶ᵔ▽ᵔ˶)",
    "insult": "(ಥ﹏ಥ)",
    "dead": "(x_x)"
}

# tama class
class Tamagotchi:
    def __init__(self, name):
        self.name = name

        # stats
        self.hunger = 100
        self.happiness = 100
        self.energy = 100

        self.age_seconds = 0
        self.alive = True

        self.last_update = time.time()
        self.last_action = "idle"

    def _clamp(self, v):
        return max(0, min(100, v))

    def adjust(self, field, amount):
        setattr(self, field, self._clamp(getattr(self, field) + amount))

        # death
        if self.hunger <= 0 or self.energy <= 0:
            self.alive = False

    # get mood from stats
    def mood(self):
        if not self.alive:
            return "dead"
        score = self.happiness + self.energy - self.hunger
        if 140 <= score <= 300:
            return "happy"
        if 90 <= score <= 139:
            return "chillin"
        if 40 <= score <= 89:
            return "meh"
        if 1 <= score <= 39:
            return "grumpy"

    # decay
    def update(self):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        decay_rate = dt * 0.01

        self.adjust("hunger", -decay_rate)
        self.adjust("energy", -decay_rate * 0.7)
        self.adjust("happiness", -decay_rate * 0.3)

        self.age_seconds += dt

# save/load
def save_pet(pet):
    data = {
        "name": pet.name,
        "hunger": pet.hunger,
        "happiness": pet.happiness,
        "energy": pet.energy,
        "age_seconds": pet.age_seconds,
        "alive": pet.alive,
        "last_update": pet.last_update,
    }
    with open(save_file, "w") as f:
        json.dump(data, f)
    
def load_pet():
    if not os.path.exists(save_file):
        return None
    try:
        with open(save_file, "r") as f:
            d = json.load(f)
        pet = Tamagotchi(d["name"])
        pet.hunger = d["hunger"]
        pet.happiness = d["happiness"]
        pet.energy = d["energy"]
        pet.age_seconds = d["age_seconds"]
        pet.alive = d["alive"]
        pet.last_update = d["last_update"]
        return pet
    except:
        return None

# ui
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def render(pet):
    clear()

    if not pet.alive:
        ascii_pet = faces["dead"]
    else:
        ascii_pet = faces.get(pet.last_action, faces["idle"])

    print(f"Your Pet: {pet.name}")
    print(f"   {ascii_pet}")
    print()
    print(f"Age: {int(pet.age_seconds)}s")
    print(f"Mood: {pet.mood()}")
    print()
    print(f"Hunger:    {int(pet.hunger)}")
    print(f"Happiness: {int(pet.happiness)}")
    print(f"Energy:    {int(pet.energy)}")
    print()
    print("Commands: feed, play, sleep, pet, insult, save, quit")
    print()

# command handler
def handle_command(cmd, pet):
    cmd = cmd.strip().lower()

    if cmd == "feed":
        pet.adjust("hunger", +20)
        pet.last_action = "feed"
        print(f"{pet.name} munches")
        time.sleep(1)

    elif cmd == "play":
        pet.adjust("happiness", +20)
        pet.adjust("energy", -10)
        pet.last_action = "play"
        print(f"You play with {pet.name}!")
        time.sleep(1)

    elif cmd == "sleep":
        pet.adjust("energy", +30)
        pet.adjust("hunger", -10)
        pet.last_action = "sleep"
        print(f"{pet.name} takes a nap")
        time.sleep(1)

    elif cmd == "pet":
        pet.adjust("happiness", +10)
        pet.last_action = "pet"
        print(f"{pet.name} enjoys the pets")
        time.sleep(1)

    elif cmd == "insult":
        pet.adjust("happiness", -20)
        pet.last_action = "insult"
        print(f"{pet.name} is offended and unhappy")
        time.sleep(1)

    elif cmd == "save":
        save_pet(pet)
        print("saved")
        time.sleep(1)

    elif cmd == "quit":
        save_pet(pet)
        print("ok bye")
        exit()

    else:
        print("what is even that")
        time.sleep(1)

# main loop
def main():
    pet = load_pet()
    if not pet:
        name = input("name your creature: ")
        pet = Tamagotchi(name)
    
    while True:
        pet.update()

        if not pet.alive:
            render(pet)
            print("nooo your pet is dead")
            save_pet(pet)
            return
        
        render(pet)

        cmd = input("> ")
        handle_command(cmd, pet)

if __name__ == "__main__":
    main()