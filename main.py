import tkinter as tk
from tkinter import ttk, messagebox


# ============================================================
# Helper Functions
# ============================================================

def parse_int_list(text):
    """
    Converts a string like: '7 0 1 2 0 3'
    into a list of integers: [7, 0, 1, 2, 0, 3]
    """
    if not text.strip():
        raise ValueError("Input cannot be empty.")

    parts = text.replace(",", " ").split()
    return [int(x) for x in parts]


def clear_table(table):
    """
    Removes all rows from a Treeview table.
    """
    for item in table.get_children():
        table.delete(item)


# ============================================================
# Virtual Memory Algorithm 1: FIFO Page Replacement
# ============================================================

def fifo_page_replacement(frames_count, reference_string):
    frames = []
    queue = []
    results = []
    hits = 0
    faults = 0

    for step, page in enumerate(reference_string, start=1):

        if page in frames:
            hits += 1
            status = "Hit"

        else:
            faults += 1
            status = "Fault"

            if len(frames) < frames_count:
                frames.append(page)
                queue.append(page)
            else:
                oldest_page = queue.pop(0)
                index = frames.index(oldest_page)
                frames[index] = page
                queue.append(page)

        frame_snapshot = frames.copy()

        while len(frame_snapshot) < frames_count:
            frame_snapshot.append("-")

        results.append({
            "step": step,
            "page": page,
            "frames": frame_snapshot,
            "status": status
        })

    return results, hits, faults


# ============================================================
# Virtual Memory Algorithm 2: Additional Reference Bit
# Implemented using Aging Counters
# ============================================================

def additional_reference_bit(frames_count, reference_string, bit_size=8):
    frames = []
    counters = {}
    results = []
    hits = 0
    faults = 0

    max_bit_value = 1 << (bit_size - 1)

    for step, page in enumerate(reference_string, start=1):

        # Shift all counters right by 1
        for p in counters:
            counters[p] = counters[p] >> 1

        if page in frames:
            hits += 1
            status = "Hit"

            # Set the leftmost bit because this page was referenced
            counters[page] = counters[page] | max_bit_value

        else:
            faults += 1
            status = "Fault"

            if len(frames) < frames_count:
                frames.append(page)
                counters[page] = max_bit_value

            else:
                # Select page with the smallest counter value
                victim_page = min(frames, key=lambda p: counters[p])
                victim_index = frames.index(victim_page)

                # Remove victim page
                del counters[victim_page]

                # Insert new page
                frames[victim_index] = page
                counters[page] = max_bit_value

        frame_snapshot = frames.copy()

        while len(frame_snapshot) < frames_count:
            frame_snapshot.append("-")

        counter_snapshot = []
        for f in frame_snapshot:
            if f == "-":
                counter_snapshot.append("-")
            else:
                counter_snapshot.append(format(counters[f], f"0{bit_size}b"))

        results.append({
            "step": step,
            "page": page,
            "frames": frame_snapshot,
            "counters": counter_snapshot,
            "status": status
        })

    return results, hits, faults


# ============================================================
# Disk Scheduling Algorithm 1: SCAN
# ============================================================

def scan_disk_scheduling(cylinders, requests, current_head, previous_head):
    direction = "right" if current_head >= previous_head else "left"

    left = sorted([r for r in requests if r < current_head])
    right = sorted([r for r in requests if r >= current_head])

    service_order = []
    head_movement_path = [current_head]

    if direction == "right":
        service_order.extend(right)

        # In SCAN, the head goes to the end of disk before reversing
        if cylinders - 1 not in service_order:
            service_order.append(cylinders - 1)

        service_order.extend(reversed(left))

    else:
        service_order.extend(reversed(left))

        # In SCAN, the head goes to the beginning of disk before reversing
        if 0 not in service_order:
            service_order.append(0)

        service_order.extend(right)

    head_movement_path.extend(service_order)

    total_seek_distance = 0
    for i in range(1, len(head_movement_path)):
        total_seek_distance += abs(head_movement_path[i] - head_movement_path[i - 1])

    return service_order, total_seek_distance, direction


# ============================================================
# Disk Scheduling Algorithm 2: C-LOOK
# ============================================================

def clook_disk_scheduling(cylinders, requests, current_head, previous_head):
    direction = "right" if current_head >= previous_head else "left"

    left = sorted([r for r in requests if r < current_head])
    right = sorted([r for r in requests if r >= current_head])

    service_order = []
    head_movement_path = [current_head]

    if direction == "right":
        # Serve requests to the right first
        service_order.extend(right)

        # Jump to the lowest request, then continue right again
        service_order.extend(left)

    else:
        # Serve requests to the left first
        service_order.extend(reversed(left))

        # Jump to the highest request, then continue left again
        service_order.extend(reversed(right))

    head_movement_path.extend(service_order)

    total_seek_distance = 0
    for i in range(1, len(head_movement_path)):
        total_seek_distance += abs(head_movement_path[i] - head_movement_path[i - 1])

    return service_order, total_seek_distance, direction


# ============================================================
# GUI Application
# ============================================================

class AdvancedOSSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced OS Algorithms Simulator")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f4f6f8")

        title = tk.Label(
            root,
            text="Advanced OS Algorithms Simulator",
            font=("Arial", 22, "bold"),
            bg="#f4f6f8",
            fg="#1f2937"
        )
        title.pack(pady=15)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=20, pady=10)

        self.create_fifo_tab()
        self.create_additional_reference_bit_tab()
        self.create_scan_tab()
        self.create_clook_tab()

    # --------------------------------------------------------
    # FIFO TAB
    # --------------------------------------------------------

    def create_fifo_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="FIFO Page Replacement")

        input_frame = ttk.LabelFrame(tab, text="Input")
        input_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(input_frame, text="Number of Frames:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.fifo_frames_entry = ttk.Entry(input_frame, width=20)
        self.fifo_frames_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(input_frame, text="Reference String:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.fifo_ref_entry = ttk.Entry(input_frame, width=70)
        self.fifo_ref_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Button(input_frame, text="Run FIFO", command=self.run_fifo).grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.fifo_table = ttk.Treeview(tab, columns=("Step", "Page", "Frames", "Status"), show="headings")
        for col in ("Step", "Page", "Frames", "Status"):
            self.fifo_table.heading(col, text=col)
            self.fifo_table.column(col, width=200, anchor="center")
        self.fifo_table.pack(fill="both", expand=True, padx=20, pady=10)

        self.fifo_summary = ttk.Label(tab, text="", font=("Arial", 12, "bold"))
        self.fifo_summary.pack(pady=10)

    def run_fifo(self):
        try:
            frames_count = int(self.fifo_frames_entry.get())
            reference_string = parse_int_list(self.fifo_ref_entry.get())

            if frames_count <= 0:
                raise ValueError("Number of frames must be greater than 0.")

            results, hits, faults = fifo_page_replacement(frames_count, reference_string)

            clear_table(self.fifo_table)

            for row in results:
                self.fifo_table.insert(
                    "",
                    "end",
                    values=(
                        row["step"],
                        row["page"],
                        " | ".join(map(str, row["frames"])),
                        row["status"]
                    )
                )

            self.fifo_summary.config(
                text=f"Total Hits: {hits}    |    Total Page Faults: {faults}"
            )

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    # --------------------------------------------------------
    # ADDITIONAL REFERENCE BIT TAB
    # --------------------------------------------------------

    def create_additional_reference_bit_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Additional Reference Bit")

        input_frame = ttk.LabelFrame(tab, text="Input")
        input_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(input_frame, text="Number of Frames:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.arb_frames_entry = ttk.Entry(input_frame, width=20)
        self.arb_frames_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(input_frame, text="Reference String:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.arb_ref_entry = ttk.Entry(input_frame, width=70)
        self.arb_ref_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Button(
            input_frame,
            text="Run Additional Reference Bit",
            command=self.run_additional_reference_bit
        ).grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.arb_table = ttk.Treeview(
            tab,
            columns=("Step", "Page", "Frames", "Reference Bits", "Status"),
            show="headings"
        )

        for col in ("Step", "Page", "Frames", "Reference Bits", "Status"):
            self.arb_table.heading(col, text=col)
            self.arb_table.column(col, width=200, anchor="center")

        self.arb_table.pack(fill="both", expand=True, padx=20, pady=10)

        self.arb_summary = ttk.Label(tab, text="", font=("Arial", 12, "bold"))
        self.arb_summary.pack(pady=10)

    def run_additional_reference_bit(self):
        try:
            frames_count = int(self.arb_frames_entry.get())
            reference_string = parse_int_list(self.arb_ref_entry.get())

            if frames_count <= 0:
                raise ValueError("Number of frames must be greater than 0.")

            results, hits, faults = additional_reference_bit(frames_count, reference_string)

            clear_table(self.arb_table)

            for row in results:
                self.arb_table.insert(
                    "",
                    "end",
                    values=(
                        row["step"],
                        row["page"],
                        " | ".join(map(str, row["frames"])),
                        " | ".join(row["counters"]),
                        row["status"]
                    )
                )

            self.arb_summary.config(
                text=f"Total Hits: {hits}    |    Total Page Faults: {faults}"
            )

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    # --------------------------------------------------------
    # SCAN TAB
    # --------------------------------------------------------

    def create_scan_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="SCAN Disk Scheduling")

        input_frame = ttk.LabelFrame(tab, text="Input")
        input_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(input_frame, text="Number of Cylinders:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.scan_cylinders_entry = ttk.Entry(input_frame, width=20)
        self.scan_cylinders_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(input_frame, text="Request Queue:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.scan_requests_entry = ttk.Entry(input_frame, width=70)
        self.scan_requests_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(input_frame, text="Current Head Position:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.scan_current_entry = ttk.Entry(input_frame, width=20)
        self.scan_current_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(input_frame, text="Previous Head Position:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.scan_previous_entry = ttk.Entry(input_frame, width=20)
        self.scan_previous_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        ttk.Button(input_frame, text="Run SCAN", command=self.run_scan).grid(row=4, column=1, padx=10, pady=10, sticky="w")

        self.scan_table = ttk.Treeview(tab, columns=("Order", "Request"), show="headings")
        self.scan_table.heading("Order", text="Order")
        self.scan_table.heading("Request", text="Served Request")
        self.scan_table.column("Order", width=200, anchor="center")
        self.scan_table.column("Request", width=300, anchor="center")
        self.scan_table.pack(fill="both", expand=True, padx=20, pady=10)

        self.scan_summary = ttk.Label(tab, text="", font=("Arial", 12, "bold"))
        self.scan_summary.pack(pady=10)

    def run_scan(self):
        try:
            cylinders = int(self.scan_cylinders_entry.get())
            requests = parse_int_list(self.scan_requests_entry.get())
            current_head = int(self.scan_current_entry.get())
            previous_head = int(self.scan_previous_entry.get())

            self.validate_disk_inputs(cylinders, requests, current_head, previous_head)

            service_order, total_seek, direction = scan_disk_scheduling(
                cylinders,
                requests,
                current_head,
                previous_head
            )

            clear_table(self.scan_table)

            for i, request in enumerate(service_order, start=1):
                self.scan_table.insert("", "end", values=(i, request))

            self.scan_summary.config(
                text=f"Direction: {direction.upper()}    |    Total Seek Distance: {total_seek}"
            )

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    # --------------------------------------------------------
    # C-LOOK TAB
    # --------------------------------------------------------

    def create_clook_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="C-LOOK Disk Scheduling")

        input_frame = ttk.LabelFrame(tab, text="Input")
        input_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(input_frame, text="Number of Cylinders:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.clook_cylinders_entry = ttk.Entry(input_frame, width=20)
        self.clook_cylinders_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(input_frame, text="Request Queue:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.clook_requests_entry = ttk.Entry(input_frame, width=70)
        self.clook_requests_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(input_frame, text="Current Head Position:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.clook_current_entry = ttk.Entry(input_frame, width=20)
        self.clook_current_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(input_frame, text="Previous Head Position:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.clook_previous_entry = ttk.Entry(input_frame, width=20)
        self.clook_previous_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        ttk.Button(input_frame, text="Run C-LOOK", command=self.run_clook).grid(row=4, column=1, padx=10, pady=10, sticky="w")

        self.clook_table = ttk.Treeview(tab, columns=("Order", "Request"), show="headings")
        self.clook_table.heading("Order", text="Order")
        self.clook_table.heading("Request", text="Served Request")
        self.clook_table.column("Order", width=200, anchor="center")
        self.clook_table.column("Request", width=300, anchor="center")
        self.clook_table.pack(fill="both", expand=True, padx=20, pady=10)

        self.clook_summary = ttk.Label(tab, text="", font=("Arial", 12, "bold"))
        self.clook_summary.pack(pady=10)

    def run_clook(self):
        try:
            cylinders = int(self.clook_cylinders_entry.get())
            requests = parse_int_list(self.clook_requests_entry.get())
            current_head = int(self.clook_current_entry.get())
            previous_head = int(self.clook_previous_entry.get())

            self.validate_disk_inputs(cylinders, requests, current_head, previous_head)

            service_order, total_seek, direction = clook_disk_scheduling(
                cylinders,
                requests,
                current_head,
                previous_head
            )

            clear_table(self.clook_table)

            for i, request in enumerate(service_order, start=1):
                self.clook_table.insert("", "end", values=(i, request))

            self.clook_summary.config(
                text=f"Direction: {direction.upper()}    |    Total Seek Distance: {total_seek}"
            )

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    def validate_disk_inputs(self, cylinders, requests, current_head, previous_head):
        if cylinders <= 0:
            raise ValueError("Number of cylinders must be greater than 0.")

        if current_head < 0 or current_head >= cylinders:
            raise ValueError("Current head position must be within cylinder range.")

        if previous_head < 0 or previous_head >= cylinders:
            raise ValueError("Previous head position must be within cylinder range.")

        for request in requests:
            if request < 0 or request >= cylinders:
                raise ValueError(f"Request {request} is outside the cylinder range.")


# ============================================================
# Main Program
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedOSSimulator(root)
    root.mainloop()