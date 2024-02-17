
import gi
import os
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw,Gdk
import subprocess

class Account:
    def __init__(self, username, email, is_default):
        self.username = username
        self.email = email
        self.is_default = is_default

    def __str__(self):
        return f"{self.username}\n{self.email}\n{self.is_default}"

class AccountManager:
    def __init__(self,main_window):
        self.accounts = []
        self.config_file_path = os.path.expanduser("~/.git_switch_config")
        self.main_window = main_window

    def emit_ui_update_signal(self):
      
       self.main_window.update_ui()


    def add_account(self, account):
        self.accounts.append(account)

    def switch_account(self, account):
        for item in self.accounts:
            if account == item:
                account.is_default = True
            else:
                item.is_default = False
        
        with open(self.config_file_path, 'w') as file:
            for item in self.accounts:
                account_data = f"Username:{item.username}\nEmail:{item.email}\nActive:{item.is_default}\n"
                file.write(account_data)
        self.emit_ui_update_signal()
        subprocess.run(['git', 'config', '--global', 'user.name', account.username])
        subprocess.run(['git', 'config', '--global', 'user.email', account.email])



class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("Git Switch")
        self.set_default_size(250, 250)
        self.current_account_index = 0
        self.accounts = []
        self.account_manager = AccountManager(main_window=self)
        self.config_file_path = os.path.expanduser("~/.git_switch_config")

        if os.path.exists(self.config_file_path) and os.stat(self.config_file_path).st_size != 0:
            self.show_account_info_screen()
        else:
            self.show_welcome_screen()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("styles.css")
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.show_account_info_screen)
       

    def show_welcome_screen(self):
        welcome_label = Gtk.Label(label="Welcome to Git Switch!")
        next_button = Gtk.Button(label="Next")
        next_button.connect("clicked", self.show_new_account_screen)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.append(welcome_label)
        vbox.append(next_button)

        self.set_child(vbox)
    def update_ui(self):
       
        self.show_account_info_screen()

    def show_new_account_screen(self, button=None):
        account_number_label  = Gtk.Label(label=f"Enter Account {self.current_account_index+1} Credential")
        username_entry = Gtk.Entry(placeholder_text="Enter Username")
        email_entry = Gtk.Entry(placeholder_text="Enter Email")


        next_button = Gtk.Button(label="Next")
        if(self.current_account_index == 0):
            next_button.connect("clicked", self.save_account_and_show_next, username_entry, email_entry,True)
        else:
            next_button.connect("clicked", self.save_account_and_show_next, username_entry, email_entry,False)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.append(account_number_label)
        vbox.append(username_entry)
        vbox.append(email_entry)
        vbox.append(next_button)

        self.set_child(vbox)

    def save_account_and_show_next(self, button, username_entry, email_entry, active_switch):
        account_data = f"Username: {username_entry.get_text()}\nEmail: {email_entry.get_text()}\nActive: {active_switch}\n"
        account = Account(username_entry.get_text(), email_entry.get_text(), active_switch)
        self.account_manager.add_account(account)

        with open(self.config_file_path, 'a') as file:
            file.write(account_data)

        self.current_account_index += 1

        if self.current_account_index < 2:
            self.show_new_account_screen()
        else:
            self.show_account_info_screen()

    def show_account_info_screen(self):
            switch_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            if len(self.account_manager.accounts)==0:
                with open(self.config_file_path, 'r') as file:
                    account_info = file.read()

                lines = account_info.split('\n')
                i = 0
                for _ in range(0, len(lines)-1, 3):
                    username_line = lines[i]
                    email_line = lines[i + 1]
                    active_line = lines[i + 2]
                    account1 = Account(username_line.split(":")[1].strip(), email_line.split(":")[1].strip(), active_line)
                    self.account_manager.add_account(account1)
                    i += 3


            account_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            index = 0
            for index, account in enumerate(self.account_manager.accounts):
                account_label = str(account)
                button = Gtk.Button(label=account_label)
                button.set_size_request(150,150)
                context = button.get_style_context()
                if(index == 0):
                    context.add_class("top-account")
                else:
                    context.add_class("bottom-account")
                
                if(isinstance(account.is_default, str)):
                    account.is_default = account.is_default.split(':')[1].strip() == 'True'
                if account.is_default:
                   context.add_class("active-account")
                else:
                   context.add_class("non-active-account")
                button.connect("clicked", lambda account_box, event=None, account=account: self.on_account_clicked(button, event, account))

                account_box.append(button)
     
            self.set_child(account_box)

    def on_account_clicked(self, widget, event, account):
        self.account_manager.switch_account(account)
        widget.queue_draw()


        #   self.Account.switch_account(account)

    # Execute your command here
    # ...

    # Update the UI if needed

    
    



    def load_accounts(self):
        pass

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def do_activate(self):
        main_window = MainWindow(application=self)
        main_window.show()

def main():

    app = MyApp(application_id="com.gitswitch.myapp")

    app.run([])

if __name__ == "__main__":
    main()


