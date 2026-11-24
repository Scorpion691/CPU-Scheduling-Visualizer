import customtkinter as ctk
import psutil
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import time

class UltimateNavyGoldScheduler(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Navy-Gold 3D CPU Engine")
        self.geometry("1350x850")
        ctk.set_appearance_mode("dark")
        
        # الألوان (Navy & Gold Theme)
        self.NAVY_DEEP = "#001f3f"
        self.NAVY_LIGHT = "#003366"
        self.GOLD_ACCENT = "#D4AF37"
        self.GOLD_BRIGHT = "#FFD700"
        self.BG_BLACK = "#050505"

        self.is_running = False
        self.current_algo = "FCFS (Non-Pre)"
        self.setup_ui()

    def setup_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=300, fg_color=self.NAVY_DEEP, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="CORE CONTROL", 
                                       font=("Orbitron", 28, "bold"), 
                                       text_color=self.GOLD_ACCENT)
        self.logo_label.pack(pady=40, padx=20)

        self.algo_menu = ctk.CTkOptionMenu(self.sidebar, 
                                          values=[
                                              "FCFS (Non-Pre)", "SJF (Non-Pre)", "Priority (Non-Pre)",
                                              "SRTF (Preemptive)", "Priority (Preemptive)", "Round Robin (Preemptive)"
                                          ],
                                          command=self.change_algo,
                                          fg_color=self.GOLD_ACCENT,
                                          button_color=self.GOLD_BRIGHT,
                                          text_color="black")
        self.algo_menu.pack(pady=20, padx=20)

        self.btn_start = ctk.CTkButton(self.sidebar, text="START ENGINE", command=self.start_sim,
                                       fg_color="#1a5c1a", hover_color="#2e8b57")
        self.btn_start.pack(pady=15, padx=30)

        self.btn_stop = ctk.CTkButton(self.sidebar, text="KILL SYSTEM", command=self.stop_sim,
                                      fg_color="#8b0000", hover_color="#ff0000")
        self.btn_stop.pack(pady=10, padx=30)

        self.status_label = ctk.CTkLabel(self.sidebar, text="STATUS: IDLE", text_color=self.GOLD_ACCENT)
        self.status_label.pack(pady=40)

        self.main_stage = ctk.CTkFrame(self, fg_color=self.BG_BLACK)
        self.main_stage.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.fig = plt.figure(facecolor=self.BG_BLACK)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_stage)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")

    def change_algo(self, choice):
        self.current_algo = choice
        self.status_label.configure(text=f"MODE: {choice}")

    def start_sim(self):
        if not self.is_running:
            self.is_running = True
            self.ani = FuncAnimation(self.fig, self.update_plot, interval=400, cache_frame_data=False)
            self.canvas.draw()

    def stop_sim(self):
        self.is_running = False
        if hasattr(self, 'ani'): self.ani.event_source.stop()

    def get_real_time_procs(self):
        procs = []
        for p in psutil.process_iter(['name', 'cpu_percent', 'nice']):
            try:
                cpu = p.info['cpu_percent']
                if cpu > 0.1:
                    # إضافة أولوية عشوائية لمحاكاة التبديل في الـ Priority بشكل ملحوظ
                    p.info['custom_priority'] = np.random.randint(1, 100)
                    procs.append(p.info)
            except: continue

        # منطق الترتيب المحدث
        if "Priority" in self.current_algo:
            # هنا ستلاحظ أن المكعبات تتبدل أماكنها بناءً على الأولوية المتغيرة
            procs = sorted(procs, key=lambda x: x['custom_priority'])
        elif "SJF" in self.current_algo or "SRTF" in self.current_algo:
            procs = sorted(procs, key=lambda x: x['cpu_percent'])
        elif "Round Robin" in self.current_algo:
            np.random.shuffle(procs)
        else: # FCFS
            procs = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)
            
        return procs[:7]

    def update_plot(self, frame):
        if not self.is_running: return
        self.ax.clear()
        self.ax.set_facecolor(self.BG_BLACK)
        self.ax.set_axis_off()
        
        procs = self.get_real_time_procs()
        colors = [self.GOLD_ACCENT, self.NAVY_LIGHT, self.GOLD_BRIGHT, "#004080", "#C0C0C0", "#856404", "#4169E1"]

        for i, p in enumerate(procs):
            x, y, z = i * 2.5, 0, 0
            dx = dy = 1.6
            dz = max(p['cpu_percent'] / 3.5, 1.2)
            
            self.ax.bar3d(x, y, z, dx, dy, dz, color=colors[i % len(colors)], 
                          alpha=0.85, edgecolor=self.GOLD_ACCENT)
            
            # عرض اسم البروسيس والأولوية إذا كان النظام Priority
            label = f"{p['name'][:8]}\nCPU:{p['cpu_percent']}%"
            if "Priority" in self.current_algo:
                label += f"\nPrio:{p['custom_priority']}"
                
            self.ax.text(x + 0.8, y, dz + 1.5, label, color='white', 
                         fontsize=8, ha='center', fontweight='bold')

        self.ax.view_init(elev=20, azim=frame * 2 % 360)
        self.ax.set_xlim(-2, 18); self.ax.set_ylim(-4, 4); self.ax.set_zlim(0, 25)
        self.canvas.draw()

if __name__ == "__main__":
    UltimateNavyGoldScheduler().mainloop()