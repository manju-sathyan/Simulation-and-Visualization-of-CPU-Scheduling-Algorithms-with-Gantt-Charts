import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import random

class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Visual Simulator")
        self.root.geometry("600x400")
        self.algorithm = tk.StringVar()
        self.process_entries = []
        self.time_quantum_entry = None
        self.build_welcome_screen()

    def build_welcome_screen(self):
        self.root.configure(bg="#add8e6")
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="\U0001F4BB Welcome to CPU Scheduling Visualizer", font=("Helvetica", 16)).pack(pady=20)
        tk.Label(self.root, text="Select a scheduling algorithm to begin:", font=("Helvetica", 12)).pack(pady=10)

        algo_dropdown = ttk.Combobox(self.root, textvariable=self.algorithm, state="readonly", width=40)
        algo_dropdown['values'] = ("First Come First Serve (FCFS)",
                                   "Shortest Job First (SJF)",
                                   "Shortest Remaining Time First (SRTF)",
                                   "Round Robin",
                                   "Priority Scheduling")
        algo_dropdown.pack(pady=10)
        algo_dropdown.current(0)

        tk.Button(self.root, text="Next", command=self.load_input_screen).pack(pady=20)

    def load_input_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=f"Selected: {self.algorithm.get()}", font=("Helvetica", 12)).grid(row=0, column=0, columnspan=4, pady=10)

        tk.Label(self.root, text="No. of Processes:").grid(row=1, column=0)
        self.num_entry = tk.Entry(self.root)
        self.num_entry.grid(row=1, column=1)

        tk.Button(self.root, text="Create Fields", command=self.create_input_fields).grid(row=1, column=2)

        if "Round Robin" in self.algorithm.get():
            tk.Label(self.root, text="Time Quantum:").grid(row=2, column=0)
            self.time_quantum_entry = tk.Entry(self.root)
            self.time_quantum_entry.grid(row=2, column=1)

    def create_input_fields(self):
        try:
            num = int(self.num_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number of processes.")
            return

        for widget in self.root.winfo_children()[5:]:
            widget.destroy()

        self.process_entries = []

        tk.Label(self.root, text="PID").grid(row=4, column=0)
        tk.Label(self.root, text="Arrival Time").grid(row=4, column=1)
        tk.Label(self.root, text="Burst Time").grid(row=4, column=2)
        if "Priority" in self.algorithm.get():
            tk.Label(self.root, text="Priority").grid(row=4, column=3)

        for i in range(num):
            pid = tk.Entry(self.root)
            at = tk.Entry(self.root)
            bt = tk.Entry(self.root)
            row_entries = [pid, at, bt]

            pid.grid(row=5 + i, column=0)
            at.grid(row=5 + i, column=1)
            bt.grid(row=5 + i, column=2)

            if "Priority" in self.algorithm.get():
                pr = tk.Entry(self.root)
                pr.grid(row=5 + i, column=3)
                row_entries.append(pr)

            self.process_entries.append(row_entries)

        tk.Button(self.root, text="Simulate", command=self.simulate).grid(row=6 + num, column=0, columnspan=4, pady=10)

    def simulate(self):
        algo = self.algorithm.get()
        processes = []

        for entry in self.process_entries:
            try:
                p = {
                    'pid': entry[0].get(),
                    'arrival': int(entry[1].get()),
                    'burst': int(entry[2].get())
                }
                if "Priority" in algo:
                    p['priority'] = int(entry[3].get())
                processes.append(p)
            except ValueError:
                messagebox.showerror("Error", "Please fill all fields correctly.")
                return

        if "FCFS" in algo:
            self.run_fcfs(processes)
        elif "SJF" in algo:
            self.run_sjf(processes)
        elif "SRTF" in algo:
            self.run_srtf(processes)
        elif "Round Robin" in algo:
            try:
                tq = int(self.time_quantum_entry.get())
                self.run_rr(processes, tq)
            except:
                messagebox.showerror("Error", "Invalid Time Quantum.")
        elif "Priority" in algo:
            self.run_priority(processes)

    def run_fcfs(self, processes):
        processes.sort(key=lambda x: x['arrival'])
        time = 0
        gantt = []
        total_wt = 0
        total_tat = 0

        for p in processes:
            start = max(time, p['arrival'])
            end = start + p['burst']
            wt = start - p['arrival']
            tat = end - p['arrival']
            total_wt += wt
            total_tat += tat
            gantt.append((p['pid'], start, end))
            time = end

        self.show_gantt_chart(gantt, total_wt / len(processes), total_tat / len(processes))

    def run_sjf(self, processes):
        processes.sort(key=lambda x: (x['arrival'], x['burst']))
        time = 0
        gantt = []
        total_wt = 0
        total_tat = 0
        completed = []

        while len(completed) < len(processes):
            available = [p for p in processes if p not in completed and p['arrival'] <= time]
            if not available:
                time += 1
                continue
            shortest = min(available, key=lambda x: x['burst'])
            start = time
            end = time + shortest['burst']
            wt = start - shortest['arrival']
            tat = end - shortest['arrival']
            total_wt += wt
            total_tat += tat
            gantt.append((shortest['pid'], start, end))
            time = end
            completed.append(shortest)

        self.show_gantt_chart(gantt, total_wt / len(processes), total_tat / len(processes))

    def run_srtf(self, processes):
        time = 0
        gantt = []
        remaining = {p['pid']: p['burst'] for p in processes}
        queue = []
        last_pid = None
        total_wt = 0
        total_tat = 0
        completed = {}

        while len(completed) < len(processes):
            arrived = [p for p in processes if p['arrival'] <= time and p['pid'] not in completed]
            if arrived:
                current = min([p for p in arrived if remaining[p['pid']] > 0], key=lambda x: remaining[x['pid']])
                if last_pid != current['pid']:
                    if last_pid is not None:
                        gantt[-1] = (gantt[-1][0], gantt[-1][1], time)
                    gantt.append((current['pid'], time, None))
                    last_pid = current['pid']
                remaining[current['pid']] -= 1
                if remaining[current['pid']] == 0:
                    completed[current['pid']] = time + 1
                time += 1
            else:
                time += 1

        if gantt[-1][2] is None:
            gantt[-1] = (gantt[-1][0], gantt[-1][1], time)

        for p in processes:
            tat = completed[p['pid']] - p['arrival']
            wt = tat - p['burst']
            total_tat += tat
            total_wt += wt

        self.show_gantt_chart(gantt, total_wt / len(processes), total_tat / len(processes))

    def run_rr(self, processes, tq):
        time = 0
        gantt = []
        total_wt = 0
        total_tat = 0
        ready = []
        remaining = {p['pid']: p['burst'] for p in processes}
        arrival_map = {p['pid']: p['arrival'] for p in processes}
        executed = []
        queue = [p for p in sorted(processes, key=lambda x: x['arrival'])]

        while queue or ready:
            ready.extend([p for p in queue if p['arrival'] <= time])
            queue = [p for p in queue if p['arrival'] > time]
            if not ready:
                time += 1
                continue
            current = ready.pop(0)
            pid = current['pid']
            bt = min(tq, remaining[pid])
            gantt.append((pid, time, time + bt))
            time += bt
            remaining[pid] -= bt
            if remaining[pid] > 0:
                ready.append(current)
            else:
                executed.append((pid, time))

        completion = dict(executed)
        for p in processes:
            tat = completion[p['pid']] - p['arrival']
            wt = tat - p['burst']
            total_tat += tat
            total_wt += wt

        self.show_gantt_chart(gantt, total_wt / len(processes), total_tat / len(processes))

    def run_priority(self, processes):
        processes.sort(key=lambda x: (x['arrival'], x['priority']))
        time = 0
        gantt = []
        completed = []
        total_wt = 0
        total_tat = 0

        while len(completed) < len(processes):
            available = [p for p in processes if p not in completed and p['arrival'] <= time]
            if not available:
                time += 1
                continue
            highest = min(available, key=lambda x: x['priority'])
            start = time
            end = time + highest['burst']
            wt = start - highest['arrival']
            tat = end - highest['arrival']
            total_wt += wt
            total_tat += tat
            gantt.append((highest['pid'], start, end))
            time = end
            completed.append(highest)

        self.show_gantt_chart(gantt, total_wt / len(processes), total_tat / len(processes))

    def show_gantt_chart(self, data, avg_wt, avg_tat):
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.set_ylim(0, 10)
        ax.set_xlim(0, data[-1][2])
        ax.set_yticks([])
        colors = {}

        for (pid, start, end) in data:
            if pid not in colors:
                colors[pid] = [random.random() for _ in range(3)]
            ax.broken_barh([(start, end - start)], (2, 6), facecolors=colors[pid])
            ax.text((start + end) / 2, 5, pid, ha='center', va='center')
            ax.text(start, 1, str(start), ha='center')
        ax.text(data[-1][2], 1, str(data[-1][2]), ha='center')

        ax.set_title(f"Gantt Chart\nAverage WT: {avg_wt:.2f}, Average TAT: {avg_tat:.2f}")
        plt.tight_layout()

        def on_close(event):
            plt.close()
            self.build_welcome_screen()

        fig.canvas.mpl_connect('close_event', on_close)
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()
