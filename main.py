"""
JAHIDER NUR v2 - Mobile App (Kivy) - Android APK
Design v2 (Jahid er bola moto): Feature gulo UPORE choto pill, majher board BORO,
nicher line CHIKON/choto, Login page BORO kore upore, rongin color design.
Features: Identity/Login, Offline Mesh Map, Devices (500m + Relay), Chat, Voice, Call, News
Local Storage: jahider_nur_data.json
"""
import json, os, hashlib, uuid, math
from collections import deque

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.clock import Clock

Window.clearcolor = (0.05, 0.09, 0.14, 1)

RANGE_M = 500
DATA_FILE = "jahider_nur_data.json"

GOLD = (1, 0.76, 0.05, 1)
TEAL = (0.18, 0.89, 0.77, 1)
DARKBTN = (0.14, 0.17, 0.24, 1)
FEAT_COLORS = {"map": (0.35, 0.75, 1, 1), "devices": (0.6, 0.47, 1, 1), "chat": GOLD,
               "news": (1, 0.42, 0.62, 1), "more": TEAL}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, encoding="utf-8") as f: return json.load(f)
        except: pass
    seeds = [("Rahim","Mirpur",300,100),("Karim","Mirpur",450,-200),("Fatima","Uttara",700,150),
             ("Hasan","Gazipur",1100,200),("Ayesha","Narayanganj",1500,100),("Imran","Tangail",1900,0),
             ("Shakib","Mymensingh",2300,100),("Nusrat","Sylhet Route",2700,0),("Tanvir","Sylhet",3100,100)]
    data = {"users": [], "peers": [{"device_id":"NUR-"+str(uuid.uuid4())[:6].upper(),"name":n,"area":a,"x":x,"y":y} for n,a,x,y in seeds],
            "messages": [], "voice_notes": [], "calls": [], "news": []}
    save_data(data); return data

def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)

def dist(a,b): return math.hypot(a["x"]-b["x"], a["y"]-b["y"])
def find_route(me, target, peers):
    nodes = {me["device_id"]: me}; nodes.update({p["device_id"]: p for p in peers})
    q = deque([me["device_id"]]); prev = {me["device_id"]: None}
    while q:
        cur = q.popleft()
        if cur == target["device_id"]: break
        for nid, node in nodes.items():
            if nid not in prev and dist(nodes[cur], node) <= RANGE_M: prev[nid]=cur; q.append(nid)
    if target["device_id"] not in prev: return None
    path=[]; cur=target["device_id"]
    while cur: path.append(nodes[cur]["name"]); cur=prev[cur]
    return list(reversed(path))

DB = load_data()
CURRENT = {"user": None}

def title_bar(title, active):
    """Uporer choto title line + feature pill gulo uporer konare"""
    outer = BoxLayout(orientation="vertical", size_hint_y=None, height=86, spacing=4)
    me = CURRENT["user"]
    who = f"  • {me['username']}" if me else ""
    outer.add_widget(Label(text=f"[b]Jahider Nur[/b]  -  {title}{who}", markup=True,
                           size_hint_y=None, height=34, font_size=17, color=GOLD, halign="left"))
    bar = BoxLayout(size_hint_y=None, height=40, spacing=5)
    for txt, scr in [("Map","map"),("Devices","devices"),("Chat","chat"),("News","news"),("More","more")]:
        if scr == active:
            b = Button(text=txt, font_size=13, bold=True, background_color=FEAT_COLORS[scr], color=(0.08,0.08,0.1,1))
        else:
            b = Button(text=txt, font_size=13, background_color=DARKBTN, color=(0.92,0.93,0.97,1))
        b.bind(on_press=lambda x, s=scr: _go(s))
        bar.add_widget(b)
    outer.add_widget(bar)
    return outer

_MANAGER = {"sm": None}
def _go(scr):
    if _MANAGER["sm"]: _MANAGER["sm"].current = scr

class LoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        lay = BoxLayout(orientation="vertical", padding=26, spacing=12)
        lay.add_widget(Label(text="JAHIDER NUR", font_size=40, bold=True, size_hint_y=None, height=58, color=GOLD))
        lay.add_widget(Label(text="Offline Mesh Network - Net Charai Cholbe", font_size=15, size_hint_y=None, height=28, color=TEAL))
        lay.add_widget(Label(text="LOGIN", font_size=24, bold=True, size_hint_y=None, height=40))
        self.name_i = TextInput(hint_text="Full Name (sudhu Register e)", size_hint_y=None, height=56, multiline=False, font_size=17)
        self.user_i = TextInput(hint_text="Username (Login ID)", size_hint_y=None, height=56, multiline=False, font_size=17)
        self.pass_i = TextInput(hint_text="Password", password=True, size_hint_y=None, height=56, multiline=False, font_size=17)
        self.msg = Label(text="", size_hint_y=None, height=32, color=(1,0.45,0.45,1), font_size=14)
        lay.add_widget(self.name_i); lay.add_widget(self.user_i); lay.add_widget(self.pass_i); lay.add_widget(self.msg)
        b1 = Button(text="LOGIN - Enter Network", size_hint_y=None, height=64, background_color=GOLD, color=(0.08,0.08,0.1,1), bold=True, font_size=19)
        b1.bind(on_press=self.do_login); lay.add_widget(b1)
        b2 = Button(text="Create New Identity (Register)", size_hint_y=None, height=52, background_color=DARKBTN, font_size=15)
        b2.bind(on_press=self.do_register); lay.add_widget(b2)
        lay.add_widget(Label(text="Internet charai cholbe - 500m mesh diye", font_size=13, size_hint_y=None, height=26, color=(0.55,0.6,0.7,1)))
        lay.add_widget(Widget())
        self.add_widget(lay)
    def do_register(self, *a):
        n,u,p = self.name_i.text.strip(), self.user_i.text.strip(), self.pass_i.text.strip()
        if not n or not u or len(p)<4: self.msg.text="Sob ghor puron korun, password kompokkhe 4"; return
        if any(x["username"].lower()==u.lower() for x in DB["users"]): self.msg.text="Username age thekei ache! Login korun"; return
        user={"device_id":"NUR-"+str(uuid.uuid4())[:6].upper(),"name":n,"username":u,
              "password":hashlib.sha256(p.encode()).hexdigest(),"x":0,"y":0}
        DB["users"].append(user); save_data(DB); self.msg.text=f"Identity toiri! Device ID: {user['device_id']} - Ekhon Login korun"
    def do_login(self, *a):
        u,p = self.user_i.text.strip(), self.pass_i.text.strip()
        for x in DB["users"]:
            if x["username"].lower()==u.lower() and x["password"]==hashlib.sha256(p.encode()).hexdigest():
                CURRENT["user"]={"device_id":x["device_id"],"name":x["name"],"username":x["username"],"x":x.get("x",0),"y":x.get("y",0)}
                self.manager.current="map"; return
        self.msg.text="Username / Password bhul!"

class MapWidget(Widget):
    def draw_map(self, me):
        self.canvas.clear()
        cx, cy = self.width/2, self.height/2
        with self.canvas:
            Color(0.96,0.66,0.1,1); Line(circle=(cx,cy,50), dash_length=4, dash_offset=3)
            Color(1,0.72,0.1,1); Ellipse(pos=(cx-11,cy-11), size=(22,22))
            for p in DB["peers"]:
                px, py = cx+(p["x"]-me["x"])/10, cy+(p["y"]-me["y"])/10
                if 15<px<self.width-15 and 15<py<self.height-15:
                    r=find_route(me,p,DB["peers"]); Color(0.2,0.9,0.4,1) if dist(me,p)<=RANGE_M else Color(0.2,0.8,0.75,1) if r else Color(0.9,0.3,0.3,1)
                    Ellipse(pos=(px-8,py-8), size=(16,16))

class MapScreen(Screen):
    def on_enter(self, *a):
        self.clear_widgets(); me=CURRENT["user"]
        lay=BoxLayout(orientation="vertical", padding=10, spacing=6)
        lay.add_widget(title_bar("Offline Navigation", "map"))
        lay.add_widget(Label(text=f"{me['name']} - {me['device_id']} - Position: {me['x']}m, {me['y']}m", size_hint_y=None, height=26, color=TEAL))
        self.mapw=MapWidget(size_hint_y=1); lay.add_widget(self.mapw)
        Clock.schedule_once(lambda dt: self.mapw.draw_map(me), 0.2)
        reach=[p for p in DB["peers"] if find_route(me,p,DB["peers"])]
        direct=[p for p in DB["peers"] if dist(me,p)<=RANGE_M]
        lay.add_widget(Label(text=f"500m Direct: {len(direct)} ti - Relay Reachable: {len(reach)} ti - Mot: {len(DB['peers'])} ti", size_hint_y=None, height=26, color=TEAL, font_size=13))
        mv=BoxLayout(size_hint_y=None, height=44, spacing=4)
        for txt,dx,dy in [("Up",0,100),("Down",0,-100),("Left",-100,0),("Right",100,0)]:
            b=Button(text=txt, background_color=DARKBTN, font_size=13); b.bind(on_press=lambda x,dx=dx,dy=dy: self.move(dx,dy)); mv.add_widget(b)
        lay.add_widget(mv); self.add_widget(lay)
    def move(self,dx,dy):
        me=CURRENT["user"]; me["x"]+=dx; me["y"]+=dy; self.on_enter()

class DevicesScreen(Screen):
    def on_enter(self, *a):
        self.clear_widgets(); me=CURRENT["user"]
        lay=BoxLayout(orientation="vertical", padding=10, spacing=6)
        lay.add_widget(title_bar(f"Devices ({len(DB['peers'])} ti)", "devices"))
        sv=ScrollView(); box=BoxLayout(orientation="vertical", size_hint_y=None, spacing=4); box.bind(minimum_height=box.setter("height"))
        for p in DB["peers"]:
            d=int(dist(me,p)); r=find_route(me,p,DB["peers"])
            st="Direct" if d<=RANGE_M else (f"Relay {len(r)-1} hop: {' > '.join(r)}" if r else "Out of Mesh")
            col = (0.3,0.95,0.5,1) if d<=RANGE_M else (TEAL if r else (1,0.5,0.5,1))
            box.add_widget(Label(text=f"{p['name']} - {p['area']} - {d}m - {st}", size_hint_y=None, height=36, color=col))
        sv.add_widget(box); lay.add_widget(sv); self.add_widget(lay)

class ChatScreen(Screen):
    def on_enter(self, *a):
        self.clear_widgets()
        lay=BoxLayout(orientation="vertical", padding=10, spacing=6)
        lay.add_widget(title_bar("Chat Messaging", "chat"))
        sv=ScrollView(); box=BoxLayout(orientation="vertical", size_hint_y=None, spacing=4); box.bind(minimum_height=box.setter("height"))
        me = CURRENT["user"]["name"] if CURRENT["user"] else ""
        for m in DB["messages"]:
            own = (m["from"] == me)
            box.add_widget(Label(text=f"{m['from']}: {m['text']}", size_hint_y=None, height=34,
                                 color=(0.55,1,0.9,1) if own else (0.65,0.85,1,1),
                                 halign="right" if own else "left"))
        sv.add_widget(box); lay.add_widget(sv)
        # Nicher line: CHIKON/choto slim input row
        row=BoxLayout(size_hint_y=None, height=44, spacing=5)
        self.inp=TextInput(hint_text="Message likhun (offline mesh diye jabe)", multiline=False, font_size=14); row.add_widget(self.inp)
        b=Button(text="Send", size_hint_x=None, width=74, background_color=GOLD, color=(0.08,0.08,0.1,1), bold=True); b.bind(on_press=self.send); row.add_widget(b)
        lay.add_widget(row); self.add_widget(lay)
    def send(self,*a):
        if self.inp.text.strip():
            DB["messages"].append({"from":CURRENT["user"]["name"],"text":self.inp.text.strip()}); save_data(DB); self.on_enter()

class NewsScreen(Screen):
    def on_enter(self, *a):
        self.clear_widgets()
        lay=BoxLayout(orientation="vertical", padding=10, spacing=6)
        lay.add_widget(title_bar("News Portal", "news"))
        sv=ScrollView(); box=BoxLayout(orientation="vertical", size_hint_y=None, spacing=4); box.bind(minimum_height=box.setter("height"))
        for n in reversed(DB["news"]):
            box.add_widget(Label(text=f"{n['title']}  - {n['author']}", size_hint_y=None, height=38, color=(1,0.75,0.85,1)))
        sv.add_widget(box); lay.add_widget(sv)
        row=BoxLayout(size_hint_y=None, height=44, spacing=5)
        self.inp=TextInput(hint_text="News headline likhun - shobai post korte parbe", multiline=False, font_size=14); row.add_widget(self.inp)
        b=Button(text="Post", size_hint_x=None, width=74, background_color=(1,0.42,0.62,1), bold=True); b.bind(on_press=self.post); row.add_widget(b)
        lay.add_widget(row); self.add_widget(lay)
    def post(self,*a):
        if self.inp.text.strip():
            DB["news"].append({"title":self.inp.text.strip(),"author":CURRENT["user"]["name"]}); save_data(DB); self.on_enter()

class MoreScreen(Screen):
    def on_enter(self, *a):
        self.clear_widgets(); me=CURRENT["user"]
        lay=BoxLayout(orientation="vertical", padding=12, spacing=8)
        lay.add_widget(title_bar("Voice - Call - Identity", "more"))
        lay.add_widget(Label(text=f"{me['name']} - {me['device_id']}\nVoice Notes: {len(DB['voice_notes'])} ti - Calls: {len(DB['calls'])} ti", size_hint_y=None, height=54, color=TEAL))
        self.status=Label(text="", size_hint_y=None, height=36, color=(0.3,0.95,0.5,1)); lay.add_widget(self.status)
        bv=Button(text="Voice Message Pathan (15 sec note)", size_hint_y=None, height=54, background_color=DARKBTN); bv.bind(on_press=self.voice); lay.add_widget(bv)
        bc=Button(text="Call Korun (Rahim - Mesh Relay)", size_hint_y=None, height=54, background_color=DARKBTN); bc.bind(on_press=self.call); lay.add_widget(bc)
        lay.add_widget(Widget()); self.add_widget(lay)
        self.sec=0; self.timer=None
    def voice(self,*a):
        DB["voice_notes"].append({"from":CURRENT["user"]["name"],"duration":15}); save_data(DB); self.status.text="Voice message pathano hoyeche (Mesh diye)"
    def call(self,*a):
        self.sec=0; DB["calls"].append({"from":CURRENT["user"]["name"],"to":"Rahim"}); save_data(DB)
        if self.timer: self.timer.cancel()
        def tick(dt):
            self.sec+=1; self.status.text=f"Calling Rahim... {self.sec} sec (Relay Connected)"
        self.timer=Clock.schedule_interval(tick,1)

class JahiderNurApp(App):
    def build(self):
        self.title="Jahider Nur v2"
        sm=ScreenManager(); _MANAGER["sm"]=sm
        for cls,name in [(LoginScreen,"login"),(MapScreen,"map"),(DevicesScreen,"devices"),(ChatScreen,"chat"),(NewsScreen,"news"),(MoreScreen,"more")]:
            sm.add_widget(cls(name=name))
        return sm

if __name__=="__main__":
    JahiderNurApp().run()
