#!/usr/bin/env python3
"""
OSC Listener GUI
Listens for OSC messages on a specified IP address and port
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime
from pythonosc import dispatcher
from pythonosc import osc_server


class OSCListenerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OSC Listener")
        self.root.geometry("800x600")
        
        self.server = None
        self.server_thread = None
        self.is_connected = False
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Top frame for IP, Port, and Connect button
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        # IP Address
        ttk.Label(top_frame, text="IP Address:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ip_entry = ttk.Entry(top_frame, width=20)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Port
        ttk.Label(top_frame, text="Port:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.port_entry = ttk.Entry(top_frame, width=15)
        self.port_entry.insert(0, "7700")
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Connect/Disconnect button
        self.connect_btn = ttk.Button(top_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=4, padx=10, pady=5)
        
        # Status label (below IP address)
        self.status_label = ttk.Label(top_frame, text="Status: Disconnected", foreground="gray")
        self.status_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Log area frame
        log_frame = ttk.Frame(self.root, padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log label
        ttk.Label(log_frame, text="Received Messages:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Log text area with scrollbar
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Monaco", 10),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#d4d4d4",
            selectbackground="#264f78"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Bottom frame for buttons
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)
        
        # Clear button
        clear_btn = ttk.Button(bottom_frame, text="Clear Log", command=self.clear_log)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Copy button
        copy_btn = ttk.Button(bottom_frame, text="Copy to Clipboard", command=self.copy_to_clipboard)
        copy_btn.pack(side=tk.LEFT, padx=5)
        
    def log_message(self, address, args):
        """Add a formatted message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Format the message
        message = f"[{timestamp}] {address}\n"
        
        if args:
            # Format arguments nicely
            args_str = ", ".join([f"{type(arg).__name__}: {arg}" for arg in args])
            message += f"  Arguments: {args_str}\n"
        else:
            message += "  Arguments: (none)\n"
        
        message += "-" * 70 + "\n"
        
        # Insert at the end and auto-scroll
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        
    def osc_message_handler(self, address, *args):
        """Callback function for OSC messages"""
        # Schedule the log update on the main thread
        self.root.after(0, self.log_message, address, args)
        
    def start_server(self, ip_address, port):
        """Start the OSC server in a separate thread"""
        try:
            # Set up OSC dispatcher
            disp = dispatcher.Dispatcher()
            disp.map("/*", self.osc_message_handler)
            
            # Create and start OSC server
            self.server = osc_server.ThreadingOSCUDPServer((ip_address, port), disp)
            
            def serve():
                try:
                    self.server.serve_forever()
                except Exception as e:
                    if self.is_connected:
                        self.root.after(0, lambda: self.handle_server_error(str(e)))
            
            self.server_thread = threading.Thread(target=serve, daemon=True)
            self.server_thread.start()
            
            return True
        except Exception as e:
            return str(e)
    
    def stop_server(self):
        """Stop the OSC server"""
        if self.server:
            try:
                self.server.shutdown()
                self.server = None
            except:
                pass
    
    def toggle_connection(self):
        """Connect or disconnect from OSC server"""
        if not self.is_connected:
            # Connect
            ip_address = self.ip_entry.get().strip()
            if not ip_address:
                ip_address = "127.0.0.1"
            
            port_str = self.port_entry.get().strip()
            if not port_str:
                messagebox.showerror("Error", "Port number is required")
                return
            
            try:
                port = int(port_str)
                if port < 1 or port > 65535:
                    raise ValueError("Port must be between 1 and 65535")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid port number: {e}")
                return
            
            # Disable inputs while connecting
            self.ip_entry.config(state="disabled")
            self.port_entry.config(state="disabled")
            self.connect_btn.config(text="Connecting...", state="disabled")
            
            # Start server
            result = self.start_server(ip_address, port)
            
            if result is True:
                self.is_connected = True
                self.connect_btn.config(text="Disconnect", state="normal")
                self.status_label.config(text=f"Status: Connected to {ip_address}:{port}", foreground="green")
                self.log_message("System", ("Server started",))
            else:
                # Error starting server
                self.ip_entry.config(state="normal")
                self.port_entry.config(state="normal")
                self.connect_btn.config(text="Connect", state="normal")
                messagebox.showerror("Error", f"Could not start server:\n{result}")
        else:
            # Disconnect
            self.stop_server()
            self.is_connected = False
            self.connect_btn.config(text="Connect")
            self.status_label.config(text="Status: Disconnected", foreground="gray")
            self.ip_entry.config(state="normal")
            self.port_entry.config(state="normal")
            self.log_message("System", ("Server stopped",))
    
    def handle_server_error(self, error_msg):
        """Handle server errors"""
        self.is_connected = False
        self.connect_btn.config(text="Connect")
        self.status_label.config(text="Status: Disconnected", foreground="red")
        self.ip_entry.config(state="normal")
        self.port_entry.config(state="normal")
        self.log_message("System", (f"Server error: {error_msg}",))
        messagebox.showerror("Server Error", f"The server encountered an error:\n{error_msg}")
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.delete(1.0, tk.END)
    
    def copy_to_clipboard(self):
        """Copy all log content to clipboard"""
        content = self.log_text.get(1.0, tk.END)
        if content.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Copied", "Log content copied to clipboard!")
        else:
            messagebox.showinfo("Empty", "Log is empty, nothing to copy.")


def main():
    root = tk.Tk()
    app = OSCListenerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
