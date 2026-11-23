"""
JAHIDER NUR v1 - Mobile App (Kivy) - Android APK er jonno
Features: Identity/Login, Offline Mesh Map, Devices (500m + Relay), Chat, Voice, Call, News
Local Storage: jahider_nur_data.json (phone er nijer storage e)
APK banate: buildozer.spec diye - README_APK_BANGLA.md dekhun
"""
import json, os, hashlib, uuid, math, random
from collections import deque

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.clock import Clock

RANGE_M = 500
DATA_FILE = "jahider_nur_data.json"

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

def header(title):
    return Label(text=f"[b]{title}[/b]", markup=True, size_hint_y=None, height=56, font_size=22, color=(1,0.72,0.1,1))

def nav_bar(go):
    bar = BoxLayout(size_hint_y=None, height=52, spacing=4)
    for txt, scr in [("Map","map"),("Devices","devices"),("Chat","chat"),("News","news"),("More","more")]:
        b = Button(text=txt, font_size=13); b.bind(on_press=lambda x, s=scr: go(s)); bar.add_widget(b)
    return bar

class LoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        lay = BoxLayout(orientation="vertical", padding=24, spacing=10)
        lay.add_widget(Label(text="☀", font_size=54, size_hint_y=None, height=70, color=(1,0.72,0.1,1)))
        lay.add_widget(Label(text="JAHIDER NUR", font_size=30, bold=True, size_hint_y=None, height=44))
        lay.add_widget(Label(text="Offline Mesh • Net Charai Cholbe", font_size=14, size_hint_y=None, height=26, color=(0.4,0.9,0.8,1)))
        self.name_i = TextInput(hint_text="Full Name (sudhu Register e)", size_hint_y=None, height=48, multiline=False)
        self.user_i = TextInput(hint_text="Username (Login ID)", size_hint_y=None, height=48, multiline=False)
        self.pass_i = TextInput(hint_text="Password", password=True, size_hint_y=None, height=48, multiline=False)
        self.msg = Label(text="", size_hint_y=None, height=30, color=(1,0.4,0.4,1))
        lay.add_widget(self.name_i); lay.add_widget(self.user_i); lay.add_widget(self.pass_i); lay.add_widget(self.msg)
        b1 = Button(text="LOGIN - Enter Network", size_hint_y=None, height=52, background_color=(1,0.62,0.05,1), color=(0,0,0,1), bold=True)
        b1.bind(on_press=self.do_login); lay.add_widget(b1)
        b2 = Button(text="Create New Identity (Register)", size_hint_y=None, height=48)
        b2.bind(on_press=self.do_register); lay.add_widget(b2)
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
        lay.add_widget(header("Offline Navigation"))
        lay.add_widget(Label(text=f"⭐ {me['name']} • {me['device_id']} • Position: {me['x']}m, {me['y']}m", size_hint_y=None, height=26))
        self.mapw=MapWidget(size_hint_y=1); lay.add_widget(self.mapw)
        Clock.schedule_once(lambda dt: self.mapw.draw_map(me), 0.2)
        reach=[p for p in DB["peers"] if find_route(me,p,DB["peers"])]
        direct=[p for p in DB["peers"] if dist(me,p)<=RANGE_M]
        lay.add_widget(Label(text=f"500m Direct: {len(direct)} ti • Relay diye Reachable: {len(reach)} ti • Mot: {len(DB['peers'])} ti", size_hint_y=None, height=28, color=(0.4,0.9,0.8,1)))
        mv=BoxLayout(size_hint_y=None, height=50, spacing=4)
        for txt,dx,dy in [("⬆ Up",0,100),("⬇ Down",0,-100),("⬅ Left",-100,0),("➡ Right",100,0)]:
            b=Button(text=txt); b.bind(on_press=lambda x,dx=dx,dy=dy: self.move(dx,dy)); mv.add_widget(b)
        lay.add_widget(mv); lay.add_widget(nav_bar(lambda s: setattr(self.manager,"current",s))); self.add_widget(lay)
    def move(self,dx,dy):
        me=CURRENT["user"]; me["x"]+=dx; me["y"]+=dy; self.on_enter()

class DevicesScreen(Screen):
    def on_enter(self, *a):
        self.clear_widgets(); me=CURRENT["user"]
        lay=BoxLayout(orientation="vertical", padding=10, spacing=6)
        lay.add_widget(header(f"Devices ({len(DB['peers'])} ti)"))
        sv=ScrollView(); box=BoxLayout(orientation="vertical", size_hint_y=None, spacing=4); box.bind(minimum_height=box.setter("height"))
        for p in DB["peers"]:
            d=int(dist(me,p)); r=find_route(me,p,DB["peers"])
            st="Direct" if d<=RANGE_M else (f"Relay {len(r)-1} hop: {' > '.join(r)}" if r else "Out of Mesh")
            box.add_widget(Label(text=f"{p['name']} • {p['area']} • {d}m • {st}", size_hint_y=None, height=34))
        sv.add_widget(box); lay.add_widget(sv); lay.add_widget(nav_bar(lambda s: setattr(self.manager,"current",s))); self.add_widget(lay)

class ChatScreen(Screen):
    def on_enter(self, *a):
        self.clear_widgets()
        lay=BoxLayout(orientation="vertical", padding=10, spacing=6)
        lay.add_widget(header("Chat Messaging"))
        sv=ScrollView(); box=BoxLayout(orientation="vertical", size_hint_y=None, spacing=3); box.bind(minimum_height=box.setter("height"))
        for m in DB["messages"]:
            box.add_widget(Label(text=f"{m['from']}: {m['text']}", size_hint_y=None, height=30))
        sv.add_widget(box); lay.add_widget(sv)
        row=BoxLayout(size_hint_y=None, height=50, spacing=4)
        self.inp=TextInput(hint_text="Message likhun (offline mesh diye jabe)", multiline=False); row.add_widget(self.inp)
        b=Button(text="Send", size_hint_x=None, width=80); b.bind(on_press=self.send); row.add_widget(b)
        lay.add_widget(row); lay.add_widget(nav_bar(lambda s: setattr(self.manager,"current",s))); self.add_widget(lay)
    def send(self,*a):
        if self.inp.text.strip():
            DB["messages"].append({"from":CURRENT["user"]["name"],"text":self.inp.text.strip()}); save_data(DB); self.on_enter()

class NewsScreen(Screen):
    def on_enter(self, *a):
        self.clear_widgets()
        lay=BoxLayout(orientation="vertical", padding=10, spacing=6)
        lay.add_widget(header("News Portal"))
        self.inp=TextInput(hint_text="News headline likhe Post korun - shobai post korte parbe", size_hint_y=None, height=48, multiline=False); lay.add_widget(self.inp)
        b=Button(text="✍ News Post Korun", size_hint_y=None, height=46); b.bind(on_press=self.post); lay.add_widget(b)
        sv=ScrollView(); box=BoxLayout(orientation="vertical", size_hint_y=None, spacing=4); box.bind(minimum_height=box.setter("height"))
        for n in reversed(DB["news"]):
            box.add_widget(Label(text=f"📰 {n['title']}  — {n['author']}", size_hint_y=None, height=36))
        sv.add_widget(box); lay.add_widget(sv); lay.add_widget(nav_bar(lambda s: setattr(self.manager,"current",s))); self.add_widget(lay)
    def post(self,*a):
        if self.inp.text.strip():
            DB["news"].append({"title":self.inp.text.strip(),"author":CURRENT["user"]["name"]}); save_data(DB); self.on_enter()

class MoreScreen(Screen):
    def on_enter(self, *a):
        self.clear_widgets(); me=CURRENT["user"]
        lay=BoxLayout(orientation="vertical", padding=14, spacing=8)
        lay.add_widget(header("Voice • Call • Identity"))
        lay.add_widget(Label(text=f"👤 {me['name']} • 🆔 {me['device_id']}\n🎤 Voice Notes: {len(DB['voice_notes'])} ti • 📞 Calls: {len(DB['calls'])} ti", size_hint_y=None, height=52))
        self.status=Label(text="", size_hint_y=None, height=34, color=(0.3,0.95,0.5,1)); lay.add_widget(self.status)
        bv=Button(text="🎤 Voice Message Pathan (15 sec note)", size_hint_y=None, height=50); bv.bind(on_press=self.voice); lay.add_widget(bv)
        bc=Button(text="📞 Call Korun (Rahim - Mesh Relay)", size_hint_y=None, height=50); bc.bind(on_press=self.call); lay.add_widget(bc)
        lay.add_widget(nav_bar(lambda s: setattr(self.manager,"current",s))); self.add_widget(lay)
        self.sec=0; self.timer=None
    def voice(self,*a):
        DB["voice_notes"].append({"from":CURRENT["user"]["name"],"duration":15}); save_data(DB); self.status.text="🎤 Voice message pathano hoyeche (Mesh diye)"
    def call(self,*a):
        self.sec=0; DB["calls"].append({"from":CURRENT["user"]["name"],"to":"Rahim"}); save_data(DB)
        if self.timer: self.timer.cancel()
        def tick(dt):
            self.sec+=1; self.status.text=f"📞 Calling Rahim... {self.sec} sec (Relay Connected) - abar Call chaple timer cholbe, onno page e gele theme jabe"
        self.timer=Clock.schedule_interval(tick,1)

class JahiderNurApp(App):
    def build(self):
        self.title="Jahider Nur v1"
        sm=ScreenManager()
        for cls,name in [(LoginScreen,"login"),(MapScreen,"map"),(DevicesScreen,"devices"),(ChatScreen,"chat"),(NewsScreen,"news"),(MoreScreen,"more")]:
            sm.add_widget(cls(name=name))
        return sm

if __name__=="__main__":
    JahiderNurApp().run()
