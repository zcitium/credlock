import customtkinter as ctk
from tkinter import messagebox
import pyperclip
import crypto
import db

# Neon Colors
BG_COLOR = "#0D0D11"
FRAME_COLOR = "#15161C"
ACCENT_CYAN = "#00F3FF"
ACCENT_PINK = "#FF0055"
TEXT_COLOR = "#EFEFEF"
FONT_FAMILY = "Consolas"

class NeonButton(ctk.CTkButton):
    def __init__(self, master, is_danger=False, **kwargs):
        color = ACCENT_PINK if is_danger else ACCENT_CYAN
        hover = "#CC0044" if is_danger else "#00C2CC"
        super().__init__(
            master,
            fg_color=color,
            hover_color=hover,
            text_color="#000000",
            font=ctk.CTkFont(family=FONT_FAMILY, weight="bold"),
            corner_radius=4,
            **kwargs
        )

class OutlineButton(ctk.CTkButton):
    def __init__(self, master, is_danger=False, **kwargs):
        color = ACCENT_PINK if is_danger else ACCENT_CYAN
        hover = "#CC0044" if is_danger else "#00C2CC"
        super().__init__(
            master,
            fg_color="transparent",
            border_width=2,
            border_color=color,
            hover_color=hover,
            text_color=color,
            font=ctk.CTkFont(family=FONT_FAMILY, weight="bold"),
            corner_radius=4,
            **kwargs
        )

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CredLock")
        self.geometry("700x600")
        self.resizable(False, False)
        
        # Apply Neon Theme globally
        self.configure(fg_color=BG_COLOR)
        
        self.master_key = None
        self.user_id = None
        self.username = None
        
        self.container = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        db.init_db()
        self.show_startup_screen()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.unbind("<Return>")

    def heading(self, text, color=ACCENT_CYAN):
        return ctk.CTkLabel(
            self.container, 
            text=text, 
            text_color=color, 
            font=ctk.CTkFont(family=FONT_FAMILY, size=28, weight="bold")
        )

    def show_startup_screen(self):
        self.clear_container()
        self.user_id = None
        self.master_key = None
        
        self.title_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.title_frame.pack(pady=(40, 5))
        
        self.title_label = self.heading("", ACCENT_CYAN)
        self.title_label.pack(in_=self.title_frame)
        
        self.subtitle_label = ctk.CTkLabel(self.container, text="", text_color=ACCENT_PINK, font=(FONT_FAMILY, 14, "bold"))
        self.subtitle_label.pack(pady=(0, 20))
        
        self._animate_title("CredLock", "Secure Vault System")
        
        users = db.get_users()
        if not users:
            ctk.CTkLabel(self.container, text="No profiles found.", text_color=TEXT_COLOR, font=(FONT_FAMILY, 14)).pack(pady=10)
        else:
            for uid, uname in users:
                NeonButton(
                    self.container, 
                    text=f"> {uname} <",
                    command=lambda i=uid, n=uname: self.show_login_screen(i, n),
                    width=250
                ).pack(pady=5)
                
        OutlineButton(
            self.container, 
            text="CREATE NEW PROFILE", 
            command=self.show_setup_screen,
            width=250
        ).pack(pady=(30, 0))

    def _animate_title(self, target_title, target_subtitle, t_idx=0, s_idx=0):
        if t_idx <= len(target_title):
            # Typewriter effect for main title
            self.title_label.configure(text=target_title[:t_idx] + ("_" if t_idx < len(target_title) else ""))
            self.after(80, self._animate_title, target_title, target_subtitle, t_idx + 1, s_idx)
        elif s_idx <= len(target_subtitle):
            # Typewriter effect for subtitle
            self.subtitle_label.configure(text=target_subtitle[:s_idx] + ("_" if s_idx < len(target_subtitle) else ""))
            self.after(40, self._animate_title, target_title, target_subtitle, t_idx, s_idx + 1)

    def show_setup_screen(self):
        self.clear_container()
        
        self.heading("CREATE NEW PROFILE", ACCENT_PINK).pack(pady=(20, 10))
        
        self.user_entry = ctk.CTkEntry(self.container, placeholder_text="Username", width=300, fg_color=FRAME_COLOR, text_color=TEXT_COLOR, border_color=ACCENT_CYAN)
        self.user_entry.pack(pady=5)
        self.user_entry.focus()
        
        self.pw1_entry = ctk.CTkEntry(self.container, placeholder_text="Password 1", show="*", width=300, fg_color=FRAME_COLOR, text_color=TEXT_COLOR, border_color=ACCENT_CYAN)
        self.pw1_entry.pack(pady=5)
        
        self.pw2_entry = ctk.CTkEntry(self.container, placeholder_text="Password 2", show="*", width=300, fg_color=FRAME_COLOR, text_color=TEXT_COLOR, border_color=ACCENT_CYAN)
        self.pw2_entry.pack(pady=5)
        
        ctk.CTkLabel(self.container, text="Recovery Question:", text_color=TEXT_COLOR, font=(FONT_FAMILY, 14)).pack(pady=(15, 0))
        self.req_q_entry = ctk.CTkEntry(self.container, placeholder_text="e.g. First pet's name?", width=300, fg_color=FRAME_COLOR, text_color=TEXT_COLOR, border_color=ACCENT_PINK)
        self.req_q_entry.pack(pady=5)
        
        self.req_a_entry = ctk.CTkEntry(self.container, placeholder_text="Recovery Answer", show="*", width=300, fg_color=FRAME_COLOR, text_color=TEXT_COLOR, border_color=ACCENT_PINK)
        self.req_a_entry.pack(pady=5)
        
        def on_enter(event=None):
            self.do_setup()
            
        self.bind("<Return>", on_enter)
        NeonButton(self.container, text="CREATE", command=self.do_setup, width=200).pack(pady=20)
        OutlineButton(self.container, text="BACK", command=self.show_startup_screen, width=200).pack()

    def do_setup(self):
        un = self.user_entry.get().strip()
        p1 = self.pw1_entry.get()
        p2 = self.pw2_entry.get()
        rq = self.req_q_entry.get()
        ra = self.req_a_entry.get()
        
        if not all([un, p1, p2, rq, ra]):
            messagebox.showerror("Error", "All fields are required!")
            return
            
        uid = db.create_user(un)
        if uid == -1:
            messagebox.showerror("Error", "Username already exists!")
            return
            
        crypto.initialize_vault(uid, p1, p2, rq, ra)
        messagebox.showinfo("Success", "Profile created successfully! Please log in.")
        self.show_login_screen(uid, un)

    def show_login_screen(self, user_id, username):
        self.clear_container()
        self.user_id = user_id
        self.username = username
        
        self.heading(f"LOGIN: {username.upper()}", ACCENT_CYAN).pack(pady=(60, 20))
        
        self.pw1_entry = ctk.CTkEntry(self.container, placeholder_text="Password 1", show="*", width=300, fg_color=FRAME_COLOR, text_color=TEXT_COLOR, border_color=ACCENT_CYAN)
        self.pw1_entry.pack(pady=10)
        self.pw1_entry.focus()
        
        self.pw2_entry = ctk.CTkEntry(self.container, placeholder_text="Password 2", show="*", width=300, fg_color=FRAME_COLOR, text_color=TEXT_COLOR, border_color=ACCENT_CYAN)
        self.pw2_entry.pack(pady=10)
        
        def on_enter(event=None):
            self.do_login()
            
        self.bind("<Return>", on_enter)
        
        NeonButton(self.container, text="ENTER VAULT", command=self.do_login, width=200).pack(pady=20)
        OutlineButton(self.container, text="FORGOT PASSWORD", command=self.show_recovery_screen, width=200).pack(pady=5)
        OutlineButton(self.container, text="SWITCH PROFILE", command=self.show_startup_screen, width=200).pack(pady=5)

    def do_login(self):
        p1 = self.pw1_entry.get()
        p2 = self.pw2_entry.get()
        
        key = crypto.unlock_vault_main(self.user_id, p1, p2)
        if key:
            self.master_key = key
            self.show_vault_screen()
        else:
            messagebox.showerror("Access Denied", "Incorrect hardware keys (passwords).")

    def show_recovery_screen(self):
        self.clear_container()
        
        question = crypto.get_recovery_question(self.user_id)
        self.heading("RESET PASSWORDS", ACCENT_PINK).pack(pady=(40, 20))
        
        ctk.CTkLabel(self.container, text=f"Query: {question}", text_color=TEXT_COLOR, font=(FONT_FAMILY, 16)).pack(pady=10)
        
        self.rec_a_entry = ctk.CTkEntry(self.container, placeholder_text="Answer", show="*", width=300, fg_color=FRAME_COLOR, text_color=TEXT_COLOR, border_color=ACCENT_PINK)
        self.rec_a_entry.pack(pady=10)
        self.rec_a_entry.focus()
        
        ctk.CTkLabel(self.container, text="New Passwords:", text_color=TEXT_COLOR, font=(FONT_FAMILY, 14)).pack(pady=(20, 0))
        self.new_pw1_entry = ctk.CTkEntry(self.container, placeholder_text="New Password 1", show="*", width=300, fg_color=FRAME_COLOR, text_color=TEXT_COLOR, border_color=ACCENT_CYAN)
        self.new_pw1_entry.pack(pady=5)
        self.new_pw2_entry = ctk.CTkEntry(self.container, placeholder_text="New Password 2", show="*", width=300, fg_color=FRAME_COLOR, text_color=TEXT_COLOR, border_color=ACCENT_CYAN)
        self.new_pw2_entry.pack(pady=5)
        
        def on_enter(event=None):
            self.do_recovery()
            
        self.bind("<Return>", on_enter)
        
        NeonButton(self.container, text="RESET PASSWORDS", command=self.do_recovery, is_danger=True, width=200).pack(pady=20)
        OutlineButton(self.container, text="CANCEL", command=lambda: self.show_login_screen(self.user_id, self.username), width=200).pack()

    def do_recovery(self):
        ans = self.rec_a_entry.get()
        np1 = self.new_pw1_entry.get()
        np2 = self.new_pw2_entry.get()
        
        if not ans or not np1 or not np2:
            messagebox.showerror("Error", "All sequence parameters required!")
            return
            
        key = crypto.unlock_vault_recovery(self.user_id, ans)
        if key:
            crypto.reset_main_passwords(self.user_id, key, np1, np2)
            messagebox.showinfo("Success", "Security clearance updated! You may now enter the vault.")
            self.show_login_screen(self.user_id, self.username)
        else:
            messagebox.showerror("Error", "Incorrect override sequence (answer)!")

    def show_vault_screen(self):
        self.clear_container()
        
        top_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 10))
        
        self.heading(f"CREDLOCK: {self.username.upper()}", ACCENT_CYAN).pack(side="left")
        
        NeonButton(top_frame, text="+ ADD NODE", command=self.show_add_credential, width=120).pack(side="right", padx=(10, 0))
        OutlineButton(top_frame, text="LOGOUT", command=self.show_startup_screen, width=80).pack(side="right")
        OutlineButton(top_frame, text="DELETE PROFILE", command=self.delete_current_profile, width=120, is_danger=True).pack(side="right", padx=10)
        
        self.vault_scroll = ctk.CTkScrollableFrame(self.container, fg_color=FRAME_COLOR)
        self.vault_scroll.pack(fill="both", expand=True, pady=10)
        
        self.load_credentials()

    def load_credentials(self):
        for widget in self.vault_scroll.winfo_children():
            widget.destroy()
            
        creds = db.get_all_credentials(self.user_id)
        if not creds:
            ctk.CTkLabel(self.vault_scroll, text="No nodes found in matrix.", text_color=TEXT_COLOR).pack(pady=20)
            return

        for idx, cred in enumerate(creds):
            cid, service, username, enc_pw = cred
            
            row = ctk.CTkFrame(self.vault_scroll, fg_color=BG_COLOR, corner_radius=6, border_width=1, border_color=ACCENT_CYAN)
            row.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(row, text=service.upper(), width=150, anchor="w", font=(FONT_FAMILY, 14, "bold"), text_color=ACCENT_CYAN).pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(row, text=username, width=150, anchor="w", text_color=TEXT_COLOR).pack(side="left", padx=10)
            
            del_n = OutlineButton(row, text="DEL", is_danger=True, width=50, command=lambda i=cid: self.delete_credential(i))
            del_n.pack(side="right", padx=10)
            
            edit_n = OutlineButton(row, text="EDIT", width=50, command=lambda i=cid, s=service, u=username, p=enc_pw: self.show_edit_credential(i, s, u, p))
            edit_n.pack(side="right", padx=5)
            
            copy_n = NeonButton(row, text="COPY", width=60, command=lambda p=enc_pw: self.copy_password(p))
            copy_n.pack(side="right", padx=5)

    def show_add_credential(self):
        self.clear_container()
        self._build_cred_form("ADD NEW NODE", None, "", "", "")

    def show_edit_credential(self, cid, service, username, encrypted_pw):
        self.clear_container()
        try:
            plain_pw = crypto.decrypt_password(self.master_key, encrypted_pw)
        except Exception as e:
            messagebox.showerror("Error", "Could not decrypt password for editing.")
            self.show_vault_screen()
            return
            
        self._build_cred_form("EDIT NODE", cid, service, username, plain_pw)

    def _build_cred_form(self, title, cid, service, username, password):
        self.heading(title, ACCENT_PINK if cid else ACCENT_CYAN).pack(pady=(40, 20))
        
        ctk.CTkLabel(self.container, text="Service Name:", text_color=TEXT_COLOR).pack(pady=(10,0))
        srv_entry = ctk.CTkEntry(self.container, width=300, fg_color=FRAME_COLOR, text_color=TEXT_COLOR, border_color=ACCENT_CYAN)
        srv_entry.insert(0, service)
        srv_entry.pack(pady=5)
        srv_entry.focus()
        
        ctk.CTkLabel(self.container, text="Username:", text_color=TEXT_COLOR).pack(pady=(10,0))
        usr_entry = ctk.CTkEntry(self.container, width=300, fg_color=FRAME_COLOR, text_color=TEXT_COLOR, border_color=ACCENT_CYAN)
        usr_entry.insert(0, username)
        usr_entry.pack(pady=5)
        
        ctk.CTkLabel(self.container, text="Password:", text_color=TEXT_COLOR).pack(pady=(10,0))
        pw_entry = ctk.CTkEntry(self.container, show="*", width=300, fg_color=FRAME_COLOR, text_color=TEXT_COLOR, border_color=ACCENT_CYAN)
        pw_entry.insert(0, password)
        pw_entry.pack(pady=5)
        
        def save(event=None):
            s = srv_entry.get().strip()
            u = usr_entry.get().strip()
            p = pw_entry.get()
            if not s or not u or not p:
                messagebox.showerror("Error", "All fields required!")
                return
            
            enc = crypto.encrypt_password(self.master_key, p)
            if cid is None:
                db.add_credential(self.user_id, s, u, enc)
            else:
                db.update_credential(cid, s, u, enc)
                
            self.show_vault_screen()
            
        self.bind("<Return>", save)
        
        NeonButton(self.container, text="SAVE", command=save, width=200).pack(pady=30)
        OutlineButton(self.container, text="CANCEL", command=self.show_vault_screen, width=200, is_danger=True).pack()

    def copy_password(self, encrypted_pw):
        try:
            plain = crypto.decrypt_password(self.master_key, encrypted_pw)
            pyperclip.copy(plain)
            messagebox.showinfo("Copied", "Data copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {e}")

    def delete_credential(self, cid):
        if messagebox.askyesno("Confirm", "Delete this credential?"):
            db.delete_credential(cid)
            self.load_credentials()

    def delete_current_profile(self):
        if messagebox.askyesno("Confirm Purge", f"WARNING: This will permanently delete the profile '{self.username.upper()}' and ALL its associated data.\n\nAre you absolutely sure?"):
            db.delete_user(self.user_id)
            messagebox.showinfo("Profile Deleted", "Profile and all associated data have been purged.")
            self.show_startup_screen()

