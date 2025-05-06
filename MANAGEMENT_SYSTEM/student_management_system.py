
import tkinter as tk

from tkinter.filedialog import askopenfilename,askdirectory
from PIL import Image, ImageTk, ImageDraw, ImageFont,ImageOps
from io import BytesIO
import re
import random
import sqlite3
import os
import win32api
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import test1

from tkinter.ttk import Combobox,Treeview
from tkinter.scrolledtext import ScrolledText
import threading

root = tk.Tk()
root.geometry("500x600")
root.title("Student Registration & Management System")
bg_color="#1fbe38"

login_stud_icon=tk.PhotoImage(file="C:\\MANAGEMENT_SYSTEM\\Images\\login_student_img.png")
login_admin_icon=tk.PhotoImage(file="C:\\MANAGEMENT_SYSTEM\\Images\\admin_img.png")
add_student_icon=tk.PhotoImage(file="C:\\MANAGEMENT_SYSTEM\\Images\\add_student_img.png")
locked_icon=tk.PhotoImage(file="C:\\MANAGEMENT_SYSTEM\\Images\\locked.png")
unlocked_icon=tk.PhotoImage(file="C:\\MANAGEMENT_SYSTEM\\Images\\unlocked.png")
add_student_pic_icon=tk.PhotoImage(file="C:\\MANAGEMENT_SYSTEM\\Images\\add_image.png")


def init_database():
    if os.path.exists('student_accounts.db'):

        connection = sqlite3.connect('student_accounts.db')

        cursor = connection.cursor()
        # table name:data column name: left side column data type:right side
        cursor.execute("""
        SELECT * FROM data
        """)

        connection.commit()
        print(cursor.fetchall())
        connection.close()


    else:

        connection = sqlite3.connect('student_accounts.db')

        cursor = connection.cursor()
#table name:data column name: left side column data type:right side
        cursor.execute("""
         CREATE TABLE data (
         id_number text,
         password text,
         name text,
         age text,
         gender text,
         phone_number text,
         class text,
         email text,
         image blob
         )
         """)


        connection.commit()
        connection.close()

def check_id_already_exists(id_number):
    connection = sqlite3.connect('student_accounts.db')
    cursor = connection.cursor()
    cursor.execute(f"""
    SELECT id_number FROM data WHERE id_number == '{id_number}'
    """)

    connection.commit()
    response=cursor.fetchall()
    connection.close()

    return response


def check_valid_password(id_number,password):
    connection = sqlite3.connect('student_accounts.db')
    cursor = connection.cursor()
    cursor.execute(f"""
    SELECT id_number,password  FROM data WHERE id_number == '{id_number}' AND password == '{password}'
    """)

    connection.commit()
    response=cursor.fetchall()
    connection.close()

    return response



def add_data(id_number,password,name,age,gender,phone_number,student_class,email,pic_data):
    connection = sqlite3.connect('student_accounts.db')
    cursor=connection.cursor()
    cursor.execute(f"""
    INSERT INTO data VALUES('{id_number}','{password}','{name}','{age}','{gender}','{phone_number}','{student_class}','{email}',?)
    """,[pic_data])

    connection.commit()
    connection.close()


def confirmation_box(message):

    answer=tk.BooleanVar()
    answer.set(False)
    def action(ans):
        answer.set(ans)
        confirmation_box_fm.destroy()

    confirmation_box_fm = tk.Frame(root,highlightbackground=bg_color,highlightthickness=3)
    message_lb = tk.Label(confirmation_box_fm, text=message, font=('Bold', 15))
    message_lb.pack(pady=20)

    cancel_btn = tk.Button(confirmation_box_fm, text="Cancel", font=('Bold', 15), bg=bg_color, fg="white",bd=0,command=lambda:action(False))
    cancel_btn.place(x=50,y=160)
    yes_btn = tk.Button(confirmation_box_fm, text="Yes", font=('Bold', 15), bg=bg_color, fg="white",bd=0,command=lambda:action(True))
    yes_btn.place(x=190,y=160,width=80)
    confirmation_box_fm.place(x=100,y=120,width=320,height=220)

    root.wait_window(confirmation_box_fm)
    return answer.get()


def message_box(message):
    message_box_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)

    close_btn=tk.Button(message_box_fm,text="X",font=('Bold',13),fg=bg_color,bd=0,command=lambda: message_box_fm.destroy())
    close_btn.place(x=290,y=5)

    message_lb = tk.Label(message_box_fm, text=message, font=('Bold', 15))
    message_lb.pack(pady=50)

    message_box_fm.place(x=100, y=120, width=320, height=220)

def draw_student_card(student_pic_path, student_data):
    labels = """
ID Number:
Name:
Gender:
Age:
Class:
Contact:
Email:    
"""
    try:
        # Load the student card template
        student_card = Image.open('C:\\MANAGEMENT_SYSTEM\\Images\\student_card_frame.png')

        # Load student picture
        try:
            # If path is empty or invalid, use default image
            if not student_pic_path or not os.path.exists(student_pic_path):
                pic = Image.open('C:\\MANAGEMENT_SYSTEM\\Images\\Student_img')
            else:
                pic = Image.open(student_pic_path)

            pic = pic.resize((110, 110))
            student_card.paste(pic, box=(15, 25))

        except Exception:
            # Fallback to default image if any error occurs
            default_pic = Image.open('C:\\student_management_system\\Images\\add_image.png')
            default_pic = default_pic.resize((110, 110))
            student_card.paste(default_pic, box=(15, 25))

        # Add text to the card
        draw = ImageDraw.Draw(student_card)
        labels_font = ImageFont.truetype(font='bahnschrift', size=18)
        heading_font = ImageFont.truetype(font='arial', size=15)
        data_font = ImageFont.truetype(font='bahnschrift', size=13)

        draw.text((150, 60), text='Student Card', fill=(0, 0, 0), font=heading_font)
        draw.multiline_text(xy=(15, 120), text=labels, fill=(0, 0, 0), font=labels_font, spacing=6)
        draw.multiline_text(xy=(120, 120), text=student_data, fill=(0, 0, 0), font=data_font, spacing=10)

        return student_card

    except Exception as e:
        raise Exception(f"Failed to create student card: {str(e)}")



def student_card_page(student_card_obj,bypass_login_page=False):

    def save_student_card():
        path = askdirectory()

        if path:
            print(path)

            student_card_obj.save(os.path.join(path, 'Student Card.png'))
            message_box('Student Card Saved Successfully!')

    def print_student_card():
        path = askdirectory()

        if path:
            print(path)

            student_card_obj.save(os.path.join(path, 'Student Card.png'))

            win32api.ShellExecute(0, 'print', os.path.join(path, 'Student Card.png'), '/d:"%s"' % 'Print to Default Printer', '.', 0)


    def close_student_card_page():
        student_card_page_fm.destroy()

        if not bypass_login_page:
            root.update()
            welcome_page()






    student_card_img=ImageTk.PhotoImage(student_card_obj)
    student_card_page_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)

    heading_lb=tk.Label(student_card_page_fm,text="Student Card",font=('Bold',18),bg=bg_color,fg="white")
    heading_lb.place(x=0,y=0,width=400)

    close_btn=tk.Button(student_card_page_fm,text="X",font=('Bold',13),bg=bg_color,fg='white',bd=0,command=close_student_card_page)
    close_btn.place(x=370,y=0)



    student_card_lb=tk.Label(student_card_page_fm,image=student_card_img)
    student_card_lb.place(x=50,y=50)
    student_card_lb.image=student_card_img



    save_student_card_btn=tk.Button(student_card_page_fm,text='Save Student Card',font=('Bold',15),bg=bg_color,fg='white',bd=1,command=save_student_card)
    save_student_card_btn.place(x=80,y=375)

    print_student_card_btn = tk.Button(student_card_page_fm, text='🖨️', font=('Bold',18), bg=bg_color,
                                      fg='white', bd=1,command=print_student_card)
    print_student_card_btn.place(x=270, y=370)
    student_card_page_fm.place(x=50,y=30,width=400,height=450)


def welcome_page():

    def forward_to_student_login_page():
        welcome_page_fm.destroy()
        root.update()
        student_login_page()

    def forward_to_admin_login_page():
        welcome_page_fm.destroy()
        root.update()
        admin_login_page()

    def forward_to_add_account_page():
        welcome_page_fm.destroy()
        root.update()
        add_account_page()

    welcome_page_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)

    heading_lb = tk.Label(welcome_page_fm, text="Welcome to\nStudent Management System", font=('Bold', 18), bg=bg_color,
                          fg="white")
    heading_lb.place(x=0, y=0, width=400)
    welcome_page_fm.pack(pady=30)
    welcome_page_fm.propagate(False)
    welcome_page_fm.config(width=400, height=420)

    student_login_btn = tk.Button(welcome_page_fm, bg=bg_color, text='Student Login', font=('Bold', 15), bd=0,
                                  fg="white",command=forward_to_student_login_page)
    student_login_btn.place(x=120, y=125, width=200)

    student_login_img = tk.Button(welcome_page_fm, image=login_stud_icon, bd=0,command=forward_to_student_login_page)
    student_login_img.place(x=60, y=100)

    admin_login_btn = tk.Button(welcome_page_fm, bg=bg_color, text='Admin Login', font=('Bold', 15), bd=0, fg="white",command=forward_to_admin_login_page)
    admin_login_btn.place(x=120, y=225, width=200)

    admin_login_img = tk.Button(welcome_page_fm, image=login_admin_icon, bd=0,command=forward_to_student_login_page)
    admin_login_img.place(x=60, y=200)

    add_student_btn = tk.Button(welcome_page_fm, bg=bg_color, text='Create Account', font=('Bold', 15), bd=0,
                                fg="white",command=forward_to_add_account_page)
    add_student_btn.place(x=120, y=325, width=200)

    add_student_img = tk.Button(welcome_page_fm, image=add_student_icon, bd=0,command=forward_to_add_account_page)
    add_student_img.place(x=60, y=300)

def sendmail_to_student(email, message,subject):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    username = test1.email_address
    password = test1.password

    msg = MIMEMultipart()

    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = email

    msg.attach(MIMEText(_text=message, _subtype='html'))

    smtp_connection = smtplib.SMTP(host=smtp_server, port=smtp_port)
    smtp_connection.starttls()
    smtp_connection.login(user=username, password=password)

    smtp_connection.sendmail(from_addr=username, to_addrs=email, msg=msg.as_string())
    print("Email sent successfully!")
    smtp_connection.quit()





def forget_password_page():
    def recover_password():
        student_id = student_id_ent.get().strip()

        if not student_id:
            custom_message_box("Please enter a Student ID")
            return

        try:
            existing_id = check_id_already_exists(id_number=student_id)
        except Exception as e:
            custom_message_box(f"Error checking ID: {str(e)}")
            return

        if existing_id:
            try:
                connection = sqlite3.connect('student_accounts.db')
                cursor = connection.cursor()

                cursor.execute("SELECT password, email FROM data WHERE id_number = ?", (student_id,))
                result = cursor.fetchone()

                if result and result[0] and result[1]:
                    recovered_password = result[0]
                    email_address = result[1]

                    def on_confirm():
                        success = send_password_email(email_address, recovered_password)
                        if success:
                            custom_message_box("Your password has been sent to your email.")
                        else:
                            custom_message_box("Failed to send email. Please try again later.")

                    email_confirmation_popup(email_address, on_confirm)
                else:
                    custom_message_box("No password or email found for this ID")

            except sqlite3.Error as e:
                custom_message_box(f"Database error: {str(e)}")

            finally:
                if connection:
                    connection.close()
        else:
            custom_message_box("Invalid ID number")

    def send_password_email(to_email, password):
        from_email = "rohithkarthik275@gmail.com"  # Replace with your Gmail
        app_password = "wvrl mwnh sawe vqls"  # Replace with your 16-character App Password

        subject = "Your Recovered Password"
        body = f"Here is your recovered password: {password}"

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(from_email, app_password)
                server.sendmail(from_email, to_email, msg.as_string())
            return True
        except Exception as e:
            print("Email sending error:", e)
            return False

    def custom_message_box(message):
        popup = tk.Toplevel(root)
        popup.geometry("300x120")
        popup.title("Info")
        popup.configure(bg='white', highlightbackground="green", highlightthickness=2)
        popup.grab_set()
        popup.transient(root)

        label = tk.Label(popup, text=message, font=('Arial', 12), bg='white', fg='black',
                         wraplength=250, justify='center')
        label.pack(pady=20)

        ok_btn = tk.Button(popup, text="OK", font=("Arial", 10, "bold"), bg='green', fg='white',
                           relief="ridge", bd=2, cursor="hand2", command=popup.destroy)
        ok_btn.pack()

    def email_confirmation_popup(email, on_confirm):
        popup = tk.Toplevel(root)
        popup.geometry("350x180")
        popup.title("Confirmation")
        popup.configure(bg='white', highlightbackground="navy", highlightthickness=3)
        popup.resizable(False, False)
        popup.grab_set()
        popup.transient(root)

        message = (
            "We will Send\n"
            "Your Forgot Password\n"
            "Via Your Email Address:\n"
            f"{email}\n"
            "Do You Want to Continue?"
        )

        msg_label = tk.Label(popup, text=message, font=("Arial", 11), bg='white', fg='black', justify='center')
        msg_label.pack(pady=15)

        btn_frame = tk.Frame(popup, bg='white')
        btn_frame.pack(pady=10)

        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Arial", 10, "bold"), bg='navy', fg='white',
                               width=10, relief="ridge", bd=2, cursor="hand2", command=popup.destroy)
        cancel_btn.grid(row=0, column=0, padx=10)

        yes_btn = tk.Button(btn_frame, text="Yes", font=("Arial", 10, "bold"), bg='navy', fg='white',
                            width=10, relief="ridge", bd=2, cursor="hand2",
                            command=lambda: [popup.destroy(), on_confirm()])
        yes_btn.grid(row=0, column=1, padx=10)

        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f"+{x}+{y}")

    # UI Frame
    forget_password_page_fm = tk.Frame(root, highlightbackground='green', highlightthickness=3)
    forget_password_page_fm.place(x=100, y=30, width=400, height=450)

    heading_lb = tk.Label(forget_password_page_fm, text="Forget Password", font=('Bold', 18), bg='green', fg="white")
    heading_lb.place(x=0, y=0, width=395)

    close_btn = tk.Button(forget_password_page_fm, text="X", font=('Bold', 13), bg='green', fg='white', bd=0,
                          command=lambda: forget_password_page_fm.destroy())
    close_btn.place(x=370, y=0)

    student_id_lb = tk.Label(forget_password_page_fm, text="Enter Student ID Number", font=('Bold', 15), fg='green')
    student_id_lb.place(x=70, y=40)

    student_id_ent = tk.Entry(forget_password_page_fm, font=('Bold', 15), justify=tk.CENTER)
    student_id_ent.place(x=70, y=70, width=180)

    info_lb = tk.Label(forget_password_page_fm, text="""We will display your\nforgotten password here""",
                       font=('Bold', 15), fg='green')
    info_lb.place(x=75, y=110)

    next_btn = tk.Button(forget_password_page_fm, text='Next', font=('Bold', 15), bg='green', fg='white',
                         command=recover_password)
    next_btn.place(x=130, y=200, width=80)


def fetch_student_data(query,params=()):
    connection = sqlite3.connect('student_accounts.db')
    cursor = connection.cursor()
    cursor.execute(query, params)
    response = cursor.fetchall()
    connection.close()
    return response


def student_dashboard(student_id):

    get_student_details = fetch_student_data(f"""SELECT name,age,gender,class,phone_number,email FROM data WHERE id_number == '{student_id}'""")

    get_student_pic = fetch_student_data(f"""SELECT image FROM data WHERE id_number == '{student_id}'""")


    student_pic = BytesIO(get_student_pic[0][0])


    def logout():
       confirm=confirmation_box(message="Do you want to logout?")

       if confirm:
           dashboard_page_fm.destroy()
           welcome_page()
           root.update()




    def switch(indicator,page):
        home_btn_indicator.config(bg="#c3c3c3")
        student_card_btn_indicator.config(bg="#c3c3c3")
        security_btn_indicator.config( bg="#c3c3c3")
        edit_data_btn_indicator.config(bg="#c3c3c3")
        delete_account_btn_indicator.config(bg="#c3c3c3")


        indicator.config(bg=bg_color)

        for child in pages_frame.winfo_children():
            child.destroy()
            root.update()

        page()


    dashboard_page_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)
    optional_frame = tk.Frame(dashboard_page_fm, highlightbackground=bg_color,highlightthickness=2,bg='#c3c3c3')


    home_btn = tk.Button(optional_frame, text="Home", font=('Bold', 15), fg=bg_color, bg="#c3c3c3", bd=0,command=lambda: switch(home_btn_indicator,page=home_page))
    home_btn.place(x=10,y=50)

    home_btn_indicator = tk.Label(optional_frame,fg=bg_color,bg="green")
    home_btn_indicator.place(x=5,y=48,width=3,height=40)

    student_card_btn = tk.Button(optional_frame, text="Student\nCard", font=('Bold', 15), fg=bg_color, bg="#c3c3c3", bd=0,justify=tk.LEFT,command=lambda: switch(student_card_btn_indicator,page=dashboard_student_card_page))
    student_card_btn.place(x=10 ,y=100)

    student_card_btn_indicator = tk.Label(optional_frame,fg=bg_color, bg="#c3c3c3")
    student_card_btn_indicator.place(x=5,y=108,width=3,height=40)

    security_btn = tk.Button(optional_frame, text="Security", font=('Bold', 15), fg=bg_color, bg="#c3c3c3",
                                 bd=0,command=lambda: switch(security_btn_indicator,page=security_page))
    security_btn.place(x=10, y=170)

    security_btn_indicator = tk.Label(optional_frame, fg=bg_color, bg="#c3c3c3")
    security_btn_indicator.place(x=5, y=170, width=3, height=40)

    edit_data_btn = tk.Button(optional_frame, text="Edit Data", font=('Bold', 15), fg=bg_color, bg="#c3c3c3",
                             bd=0,command=lambda: switch(edit_data_btn_indicator,page=edit_data_page))
    edit_data_btn.place(x=10, y=220)

    edit_data_btn_indicator = tk.Label(optional_frame, fg=bg_color, bg="#c3c3c3")
    edit_data_btn_indicator.place(x=5, y=220, width=3, height=40)

    delete_account_btn = tk.Button(optional_frame, text="Delete\nAccount", font=('Bold', 15), fg=bg_color, bg="#c3c3c3",
                             bd=0,justify=tk.LEFT,command=lambda: switch(delete_account_btn_indicator,page=delete_account_page))
    delete_account_btn.place(x=10, y=270)

    delete_account_btn_indicator = tk.Label(optional_frame, fg=bg_color, bg="#c3c3c3")
    delete_account_btn_indicator.place(x=5, y=280, width=3, height=40)

    logout_btn = tk.Button(optional_frame, text="Logout", font=('Bold', 15), fg=bg_color, bg="#c3c3c3",
                                   bd=0,command=logout)
    logout_btn.place(x=10, y=340)



    optional_frame.place(x=0,y=0,width=120,height=575)

    def home_page():

        student_pic_image_obj=Image.open(student_pic)
        size=100
        mask=Image.new(mode='L',size=(size,size))

        draw_circle=ImageDraw.Draw(im=mask)
        draw_circle.ellipse(xy=(0,0,size,size),fill=255,outline=True)

        output = ImageOps.fit(image=student_pic_image_obj,size=mask.size,centering=(1,1))
        output.putalpha(mask)
        student_picture=ImageTk.PhotoImage(output)
        home_page_fm = tk.Frame(pages_frame)

        student_pic_lb = tk.Label(home_page_fm,image=student_picture)
        student_pic_lb.image=student_picture

        student_pic_lb.place(x=10, y=10)

        hi_lb = tk.Label(home_page_fm,text=f'!Hi {get_student_details[0][0]}',font=('Bold',15))
        hi_lb.place(x=130,y=50)

        student_details=f"""
Student ID: {student_id}\n
Name: {get_student_details[0][0]}\n
Age: {get_student_details[0][1]}\n
Gender: {get_student_details[0][2]}\n
Class: {get_student_details[0][3]}\n
Phone Number: {get_student_details[0][4]}\n
Email: {get_student_details[0][5]}
"""

        student_details_lb = tk.Label(home_page_fm,text=student_details,font=('Bold',13),justify=tk.LEFT)
        student_details_lb.place(x=20,y=130)

        home_page_fm.pack(fill=tk.BOTH, expand=True)


    def dashboard_student_card_page():
        student_details = f"""
{student_id}
{get_student_details[0][0]}
{get_student_details[0][2]}
{get_student_details[0][1]}
{get_student_details[0][3]}
{get_student_details[0][4]}
{get_student_details[0][5]}
"""


        student_card_image_obj = draw_student_card(student_pic_path=student_pic,student_data=student_details)

        def save_student_card():
            path = askdirectory()

            if path:


                student_card_image_obj.save(os.path.join(path, 'Student Card.png'))
                message_box('Student Card Saved Successfully!')

        def print_student_card():
            path = askdirectory()

            if path:


                student_card_image_obj.save(os.path.join(path, 'Student Card.png'))

                win32api.ShellExecute(0, 'print', os.path.join(path, 'Student Card.png'),
                                      '/d:"%s"' % 'Print to Default Printer', '.', 0)

        student_card_img=ImageTk.PhotoImage(image=student_card_image_obj)

        student_card_page_fm = tk.Frame(pages_frame)

        card_lb = tk.Label(student_card_page_fm,image=student_card_img)
        card_lb.image=student_card_img
        card_lb.place(x=20,y=50)

        save_student_card_btn=tk.Button(student_card_page_fm,text="Save Student Card",fg="white",bg=bg_color,font=('bold',15),bd=1,command=save_student_card)
        save_student_card_btn.place(x=40,y=400)

        print_student_card_btn = tk.Button(student_card_page_fm, text="🖨️", fg="white", bg=bg_color,
                                          font=('bold', 15), bd=1, command=print_student_card)
        print_student_card_btn.place(x=240, y=400)


        student_card_page_fm.pack(fill=tk.BOTH, expand=True)


    def security_page():

        def show_hide_password():
            if current_password_ent["show"] == "*":
                current_password_ent.config(show="")
                show_hide_btn.config(image=unlocked_icon)

            else:
                current_password_ent.config(show="*")
                show_hide_btn.config(image=locked_icon)
        def set_password():
            if new_password_ent.get() != '':
                confirm=confirmation_box(message='Do You Want to Set\nNew Password?')

                if confirm:
                    connection=sqlite3.connect('student_accounts.db')

                    cursor=connection.cursor()
                    cursor.execute(f"""UPDATE data Set password= '{new_password_ent.get()}' 
                                   WHERE id_number = '{student_id}' """)

                    connection.commit()
                    connection.close()

                    message_box(message='New Password Set Successfully!')

                    current_password_ent.config(state=tk.NORMAL)
                    current_password_ent.delete(0,tk.END)
                    current_password_ent.insert(0,new_password_ent.get())
                    current_password_ent.config(state='readonly')

                    new_password_ent.delete(0,tk.END)
            else:
                message_box(message='Please Enter New Password')
        security_page_fm = tk.Frame(pages_frame)
        current_password_lb=tk.Label(security_page_fm,text="Your Current Password",font=('Bold',12))
        current_password_lb.place(x=80,y=30)

        current_password_ent=tk.Entry(security_page_fm,font=('Bold',15),justify=tk.CENTER,show='*')
        current_password_ent.place(x=50,y=80)

        student_current_password=fetch_student_data(f"""SELECT id_number,password FROM data WHERE id_number == '{student_id}'""")
        current_password_ent.insert(tk.END,student_current_password[0][0])
        current_password_ent.config(state='readonly')

        show_hide_btn = tk.Button(security_page_fm, image=locked_icon, bd=0, command=show_hide_password)
        show_hide_btn.place(x=280, y=70)

        change_password_lb=tk.Label(security_page_fm,text="Change Password",font=('Bold',15),bg='red',fg='white')
        change_password_lb.place(x=30,y=210,width=290)

        new_password_lb=tk.Label(security_page_fm,text="Set New Password",font=('Bold',12))
        new_password_lb.place(x=100,y=280)

        new_password_ent=tk.Entry(security_page_fm,font=('Bold',15),justify=tk.CENTER)
        new_password_ent.place(x=60,y=336)

        change_password_btn=tk.Button(security_page_fm,text="Set Password",font=('Bold',12),bg=bg_color,fg='white',command=set_password)
        change_password_btn.place(x=110,y=380)

        security_page_fm.pack(fill=tk.BOTH, expand=True)

    def edit_data_page():
        edit_data_page_fm = tk.Frame(pages_frame)

        pic_path = tk.StringVar()
        pic_path.set('')

        def open_pic():
            path = askopenfilename()

            if path:
                img = ImageTk.PhotoImage(Image.open(path).resize((100, 100)))
                pic_path.set(path)
                add_pic_btn.config(image=img)
                add_pic_btn.image = img

        def remove_highlight_warning(entry):
            if entry['highlightbackground'] != 'gray':
                if entry.get() != '':
                    entry.config(highlightbackground='gray', highlightcolor=bg_color)

        def check_invalid_email(email):
            pattern = r"^[a-z0-9]+([\._]?[a-z0-9]+)*@[a-z0-9]+\.[a-z]{2,4}$"
            match = re.match(pattern=pattern, string=email)
            return match

        def check_inputs():
            nonlocal get_student_details,get_student_pic,student_pic

            if student_name_ent.get() == '':
                message_box('Please Enter Student Name')
                student_name_ent.config(highlightbackground='red', highlightcolor='red')
                student_name_ent.focus()
            elif student_age_ent.get() == '':
                message_box('Please Enter Student Age')
                student_age_ent.config(highlightbackground='red', highlightcolor='red')
                student_age_ent.focus()
            elif student_contact_ent.get() == '':
                message_box('Please Enter Student Contact')
                student_contact_ent.config(highlightbackground='red', highlightcolor='red')
                student_contact_ent.focus()
            elif student_email_ent.get() == '':
                message_box('Please Enter Student Email ID')
                student_email_ent.config(highlightbackground='red', highlightcolor='red')
                student_email_ent.focus()
            elif not check_invalid_email(email=student_email_ent.get().lower()):
                student_email_ent.config(highlightbackground='red', highlightcolor='red')
                student_email_ent.focus()
                message_box(message='Invalid Email ID')
            else:
                if pic_path.get() != '':
                    new_student_picture=Image.open(pic_path.get()).resize((100,100))
                    new_student_picture.save('temp_pic.png')

                    with open('temp_pic.png', 'rb') as read_new_pic:
                        new_picture_binary=read_new_pic.read()
                        read_new_pic.close()

                    connection = sqlite3.connect('student_accounts.db')
                    cursor=connection.cursor()
                    cursor.execute(f"UPDATE data SET image=? WHERE id_number = '{student_id}' ",[new_picture_binary])

                    connection.commit()
                    connection.close()




                name=student_name_ent.get()
                age=student_age_ent.get()
                selected_class=select_class_btn.get()
                contact_number=student_contact_ent.get()
                email_address=student_email_ent.get()

                connection=sqlite3.connect('student_accounts.db')
                cursor=connection.cursor()
                cursor.execute(f"""UPDATE data SET name= '{name}', age= '{age}', class= '{selected_class}', phone_number= '{contact_number}', email= '{email_address}' WHERE id_number = '{student_id}'
                """)
                connection.commit()
                connection.close()

                get_student_details = fetch_student_data(
                    f"""SELECT name,age,gender,class,phone_number,email FROM data WHERE id_number == '{student_id}'""")

                get_student_pic = fetch_student_data(f"""SELECT image FROM data WHERE id_number == '{student_id}'""")

                student_pic = BytesIO(get_student_pic[0][0])

                message_box(message='Data Updated Successfully!')


        student_current_pic=ImageTk.PhotoImage(Image.open(student_pic))


        add_pic_section_fm = tk.Frame(edit_data_page_fm, highlightbackground=bg_color, highlightthickness=2)

        add_pic_btn = tk.Button(add_pic_section_fm, image=add_student_pic_icon, bd=0, command=open_pic)
        add_pic_btn.image=student_current_pic
        add_pic_btn.pack()

        add_pic_section_fm.place(x=5, y=5, width=105, height=105)

        student_name_lb = tk.Label(edit_data_page_fm, text="Student Name", font=('Bold', 12))
        student_name_lb.place(x=5, y=130)

        student_name_ent = tk.Entry(edit_data_page_fm, font=('Bold', 15), highlightcolor=bg_color,
                                    highlightbackground='gray', highlightthickness=2)
        student_name_ent.place(x=5, y=160, width=180)
        student_name_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_name_ent))
        student_name_ent.insert(tk.END,get_student_details[0][0])

        student_age_lb = tk.Label(edit_data_page_fm, text="Student Age", font=('Bold', 12))
        student_age_lb.place(x=5, y=210)

        student_age_ent = tk.Entry(edit_data_page_fm, font=('Bold', 15), highlightcolor=bg_color,
                                   highlightbackground='gray', highlightthickness=2)

        student_age_ent.place(x=5, y=235, width=180)
        student_age_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_age_ent))
        student_age_ent.insert(tk.END, get_student_details[0][1])

        student_contact_lb = tk.Label(edit_data_page_fm, text="Student Contact Number", font=('Bold', 12))
        student_contact_lb.place(x=5, y=285)

        student_contact_ent = tk.Entry(edit_data_page_fm, font=('Bold', 15), highlightcolor=bg_color,
                                       highlightbackground='gray', highlightthickness=2)
        student_contact_ent.place(x=5, y=310, width=180)
        student_contact_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_contact_ent))
        student_contact_ent.insert(tk.END, get_student_details[0][4])

        student_class_lb = tk.Label(edit_data_page_fm, text="Student Class", font=('Bold', 12))
        student_class_lb.place(x=5, y=360)

        select_class_btn = Combobox(edit_data_page_fm, font=('Bold', 15), state='readonly', values=class_list)
        select_class_btn.place(x=5, y=390, width=180, height=30)
        select_class_btn.set(get_student_details[0][3])

        student_email_lb = tk.Label(edit_data_page_fm, text="Student Email ID", font=('Bold', 12))
        student_email_lb.place(x=5, y=440)

        student_email_ent = tk.Entry(edit_data_page_fm, font=('Bold', 15), highlightcolor=bg_color,
                                     highlightbackground='gray', highlightthickness=2)
        student_email_ent.place(x=5, y=470, width=180)
        student_email_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_email_ent))
        student_email_ent.insert(tk.END, get_student_details[0][-1])

        update_data_btn=tk.Button(edit_data_page_fm,text="Update",font=('Bold',12),bg=bg_color,fg='white',bd=0,command=check_inputs)
        update_data_btn.place(x=220,y=470,width=80)


        edit_data_page_fm.pack(fill=tk.BOTH, expand=True)

    def delete_account_page():

        def confirm_delete_account():
            confirm=confirmation_box(message='Do You Want to\ndelete Account?')

            if confirm:
                connection=sqlite3.connect('student_accounts.db')
                cursor=connection.cursor()
                cursor.execute(f"""DELETE FROM data WHERE id_number == '{student_id}' """)

                connection.commit()
                connection.close()

                dashboard_page_fm.destroy()
                welcome_page()
                root.update()
                message_box(message='Account Deleted Successfully!')

        delete_account_page_fm = tk.Frame(pages_frame)

        delete_account_lb=tk.Label(delete_account_page_fm,text="Delete Account",font=('Bold',15),bg='red',fg='white')
        delete_account_lb.place(x=30,y=100,width=290)

        delete_account_button=tk.Button(delete_account_page_fm,text="Delete Account",font=('Bold',13),fg='white',bg='red',bd=0,command=confirm_delete_account)
        delete_account_button.place(x=100,y=150)
        delete_account_button.place(x=110,y=200)

        delete_account_page_fm.pack(fill=tk.BOTH, expand=True)

    pages_frame = tk.Frame(dashboard_page_fm)
    pages_frame.place(x=122,y=5,width=350,height=550)
    home_page()


    dashboard_page_fm.pack(pady=5)
    dashboard_page_fm.propagate(False)
    dashboard_page_fm.config(width=480, height=580)


def student_login_page():

    def show_hide_password():
        if password_ent["show"] == "*":
            password_ent.config(show="")
            show_hide_btn.config(image=unlocked_icon)

        else:
            password_ent.config(show="*")
            show_hide_btn.config(image=locked_icon)

    def forward_to_welcome_page():
        student_login_page_fm.destroy()
        root.update()
        welcome_page()


    def remove_highlight_warning(entry):
        if entry['highlightbackground']!='gray':
            if entry.get()!='':
                entry.config(highlightbackground='gray',highlightcolor=bg_color)

    def login_account():
        verify_id_number = check_id_already_exists(id_number=id_number_ent.get())

        if verify_id_number:


            verify_password = check_valid_password(id_number=id_number_ent.get(), password=password_ent.get())

            if verify_password:
                id_number=id_number_ent.get()

                student_login_page_fm.destroy()
                student_dashboard(student_id=id_number)
                root.update()

            else:
                print('oops! Password is Incorrect')
                password_ent.config(highlightbackground='red', highlightcolor='red')
                message_box(message='Please Enter Valid Password')
        else:
            print('ID is Incorrect')
            id_number_ent.config(highlightbackground='red', highlightcolor='red')

            message_box(message='Please Enter Valid ID Number')


    student_login_page_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)
    student_login_page_fm.pack(pady=30)

    student_icon_lb = tk.Label(student_login_page_fm, image=login_stud_icon, bd=0)
    student_icon_lb.place(x=150, y=40)

    id_number_lb = tk.Label(student_login_page_fm, text="Enter Student ID Number", font=('Bold', 15), fg=bg_color)
    id_number_lb.place(x=80, y=140)

    id_number_ent = tk.Entry(student_login_page_fm, font=('Bold', 15), justify=tk.CENTER, highlightcolor=bg_color,
                             highlightbackground='gray', highlightthickness='3')
    id_number_ent.place(x=80, y=190)
    id_number_ent.bind('<KeyRelease>', lambda event: remove_highlight_warning(entry=id_number_ent))

    password_lb = tk.Label(student_login_page_fm, text="Enter Student Password", font=('Bold', 15), fg=bg_color)
    password_lb.place(x=80, y=240)

    password_ent = tk.Entry(student_login_page_fm, font=('Bold', 15), justify=tk.CENTER, highlightcolor=bg_color,
                            highlightbackground='gray', highlightthickness='3', show='*')
    password_ent.place(x=80, y=290)

    password_ent.bind('<KeyRelease>', lambda event: remove_highlight_warning(entry=password_ent))

    show_hide_btn = tk.Button(student_login_page_fm, image=locked_icon, bd=0, command=show_hide_password)
    show_hide_btn.place(x=310, y=280)

    login_btn = tk.Button(student_login_page_fm, text="Login", font=('Bold', 15), bg=bg_color, fg="white",
                          command=login_account)
    login_btn.place(x=95, y=340, width=200, height=40)

    forget_password_btn = tk.Button(student_login_page_fm, text="👍\nForgot Password?", fg=bg_color, bd=0,command=forget_password_page)
    forget_password_btn.place(x=150, y=390)

    heading_lb = tk.Label(student_login_page_fm, text="Student Login Page", font=('Bold', 18), bg=bg_color, fg="white")
    heading_lb.place(x=0, y=0, width=400)

    back_btn=tk.Button(student_login_page_fm,text="←",font=('Bold',20),fg=bg_color,bd=0,command=forward_to_welcome_page)
    back_btn.place(x=5,y=40)

    student_login_page_fm.pack(pady=30)
    student_login_page_fm.propagate(False)
    student_login_page_fm.config(width=400, height=450)

def admin_dashboard():

    def switch(indicator,page):
        home_btn_indicator.config(bg='#c3c3c3')
        find_student_btn_indicator.config(bg='#c3c3c3')
        announcement_btn_indicator.config(bg='#c3c3c3')

        indicator.config(bg=bg_color)

        for child in pages_fm.winfo_children():
            child.destroy()
            root.update()

        page()



    dashboard_fm=tk.Frame(root,highlightbackground=bg_color,highlightthickness=3)

    options_fm=tk.Frame(dashboard_fm,highlightbackground=bg_color,highlightthickness=3,bg='#c3c3c3')
    options_fm.place(x=0,y=0,width=120,height=575)

    home_btn=tk.Button(dashboard_fm,text='Home',font=('Bold',15),fg=bg_color,bd=0,bg='#c3c3c3',command=lambda:switch(indicator=home_btn_indicator,page=home_page))
    home_btn.place(x=10,y=50)

    home_btn_indicator=tk.Label(options_fm,text='',bg=bg_color)
    home_btn_indicator.place(x=5,y=45,width=3,height=40)

    find_student_btn=tk.Button(dashboard_fm,text='Find\nStudent',font=('Bold',15),fg=bg_color,bd=0,bg='#c3c3c3',justify=tk.LEFT,command=lambda:switch(indicator=find_student_btn_indicator,page=find_student_page))
    find_student_btn.place(x=10,y=100)

    find_student_btn_indicator=tk.Label(options_fm,text='',bg='#c3c3c3')
    find_student_btn_indicator.place(x=5,y=100,width=3,height=40)

    announcement_btn=tk.Button(dashboard_fm,text='Announce\n-ment',font=('Bold',15),fg=bg_color,bd=0,bg='#c3c3c3',command=lambda:switch(indicator=announcement_btn_indicator,page=announcement_page))
    announcement_btn.place(x=10,y=170)

    announcement_btn_indicator=tk.Label(options_fm,text='',bg='#c3c3c3')
    announcement_btn_indicator.place(x=5,y=180,width=3,height=40)

    def logout():
        confirm = confirmation_box(message="Do You Want to\nLogout")

        if confirm:
            dashboard_fm.destroy()
            welcome_page()
            root.update()
    logout_btn=tk.Button(dashboard_fm,text='Logout',font=('Bold',15),fg=bg_color,bd=0,bg='#c3c3c3',command=logout)
    logout_btn.place(x=10,y=240)

    def home_page():
       home_page_fm=tk.Frame(pages_fm)
       admin_icon_lb=tk.Label(home_page_fm,image=login_admin_icon)
       admin_icon_lb.image=login_admin_icon
       admin_icon_lb.place(x=10,y=10)

       hi_lb=tk.Label(home_page_fm,text='!Hi Admin',font=('Bold',15))
       hi_lb.place(x=120,y=40)

       class_list_lb=tk.Label(home_page_fm,text='No.of Students By Class.',font=('Bold',13),bg=bg_color,fg='white')
       class_list_lb.place(x=20,y=130)

       students_number_lb=tk.Label(home_page_fm,text='',font=('Bold',13),justify=tk.LEFT)
       students_number_lb.place(x=20,y=170)

       for i in class_list:
           result=fetch_student_data(query=f"SELECT COUNT(*) FROM data WHERE class == '{i}' ")
           students_number_lb['text'] += f"{i} Class: {result[0][0]}\n\n"
           print(i,result)


       home_page_fm.pack(fill=tk.BOTH,expand=True)
    def find_student_page():

        def find_student():

            found_data=''


            if find_by_option_btn.get() == 'id':
                found_data=fetch_student_data(query=f"""
            SELECT id_number , name , class , gender FROM data
            WHERE id_number == '{search_input.get()}'
                """)
                print(found_data)

            elif find_by_option_btn.get() == 'name':
                found_data=fetch_student_data(query=f"""
            SELECT id_number , name , class , gender FROM data
            WHERE name LIKE '%{search_input.get()}%'
                """)
                print(found_data)

            elif find_by_option_btn.get() == 'class':
                found_data=fetch_student_data(query=f"""
            SELECT id_number , name , class , gender FROM data
            WHERE class == '{search_input.get()}'
                """)
                print(found_data)

            elif find_by_option_btn.get() == 'gender':
                found_data=fetch_student_data(query=f"""
            SELECT id_number , name , class , gender FROM data
            WHERE gender== '{search_input.get()}'
                """)
                print(found_data)

            if found_data:

                for item in record_table.get_children():
                    record_table.delete(item)

                for details in found_data:

                    record_table.insert(parent='',index='end',values=details)

            else:
                for item in record_table.get_children():
                    record_table.delete(item)


        def generate_student_card():
            selection = record_table.selection()
            selected_id = record_table.item(item=selection, option='values')[0]

            get_student_details = fetch_student_data(
            "SELECT name,age,gender,class,phone_number,email FROM data WHERE id_number =?" ,(selected_id,))

            get_student_pic = fetch_student_data(
            "SELECT image FROM data WHERE id_number ==?",(selected_id,))

            student_pic = BytesIO(get_student_pic[0][0])

            student_details = f"""
{selected_id}
{get_student_details[0][0]}
{get_student_details[0][2]}
{get_student_details[0][1]}
{get_student_details[0][3]}
{get_student_details[0][4]}
{get_student_details[0][5]}
            """

            student_card_image_obj = draw_student_card(student_pic_path=student_pic, student_data=student_details)

            student_card_page(student_card_obj=student_card_image_obj,bypass_login_page=True)

        def clear_result():
            find_by_option_btn.set('id')

            search_input.delete(0, tk.END)

            for item in record_table.get_children():
                record_table.delete(item)

            generate_student_card_btn.config(state=tk.DISABLED)


        search_filters=['id' , 'name', 'class', 'gender']
        find_student_page_fr=tk.Frame(pages_fm)
        find_student_record_lb=tk.Label(find_student_page_fr,text='Find Student Record',font=('Bold',13),fg='white',bg=bg_color)
        find_student_record_lb.place(x=20,y=10,width=300)

        find_by_lb=tk.Label(find_student_page_fr,text='Find By:',font=('Bold',12))
        find_by_lb.place(x=15,y=50)

        find_by_option_btn=Combobox(find_student_page_fr,font=('Bold',12),state='readonly',values=search_filters)
        find_by_option_btn.place(x=80,y=50,width=80)
        find_by_option_btn.set('id')

        search_input=tk.Entry(find_student_page_fr,font=('Bold',12))
        search_input.place(x=20,y=90)
        search_input.bind('<KeyRelease>' , lambda e: find_student())

        record_table_lb=tk.Label(find_student_page_fr,text='Record Table',font=('Bold',12),bg=bg_color,fg='white')
        record_table_lb.place(x=20,y=160,width=300)

        record_table=Treeview(find_student_page_fr)
        record_table.place(x=0,y=200,width=350)
        record_table.bind('<<TreeviewSelect>>',lambda e: generate_student_card_btn.config(state=tk.NORMAL))

        record_table['columns']=('id','name','class','gender')
        record_table.column('#0',width=0,stretch=tk.NO)
        record_table.heading('id', text='ID Number', anchor=tk.W)
        record_table.column('id', width=50,anchor=tk.W)
        record_table.heading('name', text='Name', anchor=tk.W)
        record_table.column('name', width=90, anchor=tk.W)
        record_table.heading('class', text='Class', anchor=tk.W)
        record_table.column('class', width=40, anchor=tk.W)
        record_table.heading('gender', text='Gender', anchor=tk.W)
        record_table.column('gender', width=40, anchor=tk.W)

        generate_student_card_btn=tk.Button(find_student_page_fr,text='Generate Student Card',font=('Bold',13),fg='white',bg=bg_color,state=tk.DISABLED,command=generate_student_card)
        generate_student_card_btn.place(x=160,y=450)
        clear_btn=tk.Button(find_student_page_fr,text='Clear',font=('Bold',13),fg='white',bg=bg_color,command=clear_result)
        clear_btn.place(x=10,y=450)





        find_student_page_fr.pack(fill=tk.BOTH,expand=True)

    def announcement_page():
        selected_classes = []

        def add_class(name):
            if selected_classes.count(name):
                selected_classes.remove(name)
            else:
                selected_classes.append(name)
            print(selected_classes)

        def collect_emails():

            fetched_emails=[]
            for _class in selected_classes:
                emails = fetch_student_data(f"SELECT email FROM data WHERE class =='{_class}'")


                for email_address in emails:
                    fetched_emails.append(*email_address)

            thread = threading.Thread(target=send_announcement,args=[fetched_emails])
            thread.start()

        def send_announcement(email_address):

            box_fm=tk.Frame(root,highlightbackground=bg_color,highlightthickness=3)

            heading_lb = tk.Label(box_fm,text='Sending Email',font=('Bold',15),bg=bg_color,fg='white')

            heading_lb.place(x=0,y=0,width=300)

            sending_lb=tk.Label(box_fm,font=('Bold',12),justify=tk.LEFT)
            sending_lb.pack(pady=50)

            box_fm.place(x=100,y=120,width=300,height=200)

            subject=announcement_subject.get()
            message=f"<h3 style='white-space: pre-wrap;'>{announcement_message.get('0.1',tk.END)}</h3>"

            sent_count=0

            for email in email_address:

                sending_lb.config(text=f"Sending To:\n{email}\n\n{sent_count}/{len(email_address)}")
                sendmail_to_student(email=email,subject=subject,message=message)

                sent_count+=1
                sending_lb.config(text=f"Sending To:\n{email}\n\n{sent_count}/{len(email_address)}")


            box_fm.destroy()
            message_box(message="Announcement Sent\nSuccessfully")


        announcement_page_fm = tk.Frame(pages_fm)

        subject_lb = tk.Label(announcement_page_fm, text='Enter Announcement Subject.', font=('Bold', 12))
        subject_lb.place(x=10, y=10)

        announcement_subject = tk.Entry(announcement_page_fm, font=('Bold', 12))
        announcement_subject.place(x=10, y=40, width=210, height=25)

        announcement_message = ScrolledText(announcement_page_fm, font=('Bold', 12))
        announcement_message.place(x=10, y=100, width=300, height=200)

        classes_list_lb = tk.Label(announcement_page_fm, text='Select Classes to Announce', font=('Bold', 12))
        classes_list_lb.place(x=10, y=320)

        y_position = 350
        for grade in class_list:
            class_check_btn = tk.Checkbutton(
                announcement_page_fm,
                text=f'Class {grade}',
                command=lambda grade = grade: add_class(name=grade)
            )
            class_check_btn.place(x=10, y=y_position)
            y_position += 25

        send_announcement_btn = tk.Button(
            announcement_page_fm,
            text='Send Announcement',
            font=('Bold', 12),
            bg=bg_color,
            fg='white',
            command=collect_emails
        )
        send_announcement_btn.place(x=180, y=520)

        announcement_page_fm.pack(fill=tk.BOTH, expand=True)
    pages_fm=tk.Frame(dashboard_fm,bg='gray')
    pages_fm.place(x=122,y=5,width=350,height=550)

    home_page()


    dashboard_fm.pack(pady=5)
    dashboard_fm.propagate(False)
    dashboard_fm.config(width=480, height=580)

def admin_login_page():
    def show_hide_password():
        if password_ent["show"] == "*":
            password_ent.config(show="")
            show_hide_btn.config(image=unlocked_icon)

        else:
            password_ent.config(show="*")
            show_hide_btn.config(image=locked_icon)

    def forward_to_welcome_page():
        admin_login_page_fm.destroy()
        root.update()
        welcome_page()
    def login_account():
        if username_ent.get() == 'admin':
            if password_ent.get() == 'admin':
                admin_login_page_fm.destroy()
                root.update()
                admin_dashboard()
            else:
                message_box(message='Please Enter Valid Password')
        else:
            message_box(message='Please Enter Valid Username')

    admin_login_page_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)

    heading_lb = tk.Label(admin_login_page_fm, text="Admin Login Page", font=('Bold', 18), bg=bg_color, fg="white")
    heading_lb.place(x=0, y=0, width=400)

    admin_icon_lb = tk.Label(admin_login_page_fm, image=login_admin_icon, bd=0)
    admin_icon_lb.place(x=150, y=40)

    username_lb = tk.Label(admin_login_page_fm, text="Enter Admin ID Number", font=('Bold', 15), fg=bg_color)
    username_lb.place(x=80, y=140)

    username_ent = tk.Entry(admin_login_page_fm, font=('Bold', 15), justify=tk.CENTER, highlightcolor=bg_color,
                            highlightbackground='gray', highlightthickness='3')
    username_ent.place(x=80, y=190)

    password_lb = tk.Label(admin_login_page_fm, text="Enter Admin Password", font=('Bold', 15), fg=bg_color)
    password_lb.place(x=80, y=240)

    password_ent = tk.Entry(admin_login_page_fm, font=('Bold', 15), justify=tk.CENTER, highlightcolor=bg_color,
                            highlightbackground='gray', highlightthickness='3', show='*')
    password_ent.place(x=80, y=290)

    show_hide_btn = tk.Button(admin_login_page_fm, image=locked_icon, bd=0, command=show_hide_password)
    show_hide_btn.place(x=310, y=280)

    login_btn = tk.Button(admin_login_page_fm, text="Login", font=('Bold', 15), bg=bg_color, fg="white",
                          command=login_account)
    login_btn.place(x=95, y=340, width=200, height=40)

    forget_password_btn = tk.Button(admin_login_page_fm, text="👍\nForgot Password?", fg=bg_color, bd=0)
    forget_password_btn.place(x=150, y=390)

    back_btn = tk.Button(admin_login_page_fm, text="←", font=('Bold', 20), fg=bg_color, bd=0,
                         command=forward_to_welcome_page)
    back_btn.place(x=5, y=40)

    admin_login_page_fm.pack(pady=30)
    admin_login_page_fm.propagate(False)
    admin_login_page_fm.config(width=400, height=450)

student_gender=tk.StringVar()
class_list=['5th','6th','7th','8th','9th','10th','11th','12th']

def add_account_page():

    pic_path=tk.StringVar()
    pic_path.set('')
    def open_pic():
        path=askopenfilename()

        if path:
            img=ImageTk.PhotoImage(Image.open(path).resize((100, 100)))
            pic_path.set(path)
            add_pic_btn.config(image=img)
            add_pic_btn.image=img
    def forward_to_welcome_page():

        ans=confirmation_box(message='Do You Want To Leave\nRegistration Form')
        if ans:
            add_account_page_fm.destroy()
            root.update()
            welcome_page()

    def remove_highlight_warning(entry):
        if entry['highlightbackground']!='gray':
            if entry.get()!='':
                entry.config(highlightbackground='gray',highlightcolor=bg_color)

    def check_invalid_email(email):
        pattern = r"^[a-z0-9]+([\._]?[a-z0-9]+)*@[a-z0-9]+\.[a-z]{2,4}$"
        match=re.match(pattern=pattern,string=email)
        return  match

    def generate_id_number():
       generated_id=''

       for r in range(6):
           generated_id += str(random.randint(0, 9))


       if not check_id_already_exists(id_number=generated_id):
           print('id_number: ', generated_id)

           student_id.config(state=tk.NORMAL)
           student_id.delete(0, tk.END)
           student_id.insert(tk.END, generated_id)
           student_id.config(state='readonly')
       else:
           generate_id_number()


    def check_input_validation():
        if student_name_ent.get()=='':
            student_name_ent.config(highlightbackground='red',highlightcolor='red')
            student_name_ent.focus()
            message_box(message='Student Name is Required')
        elif student_age_ent.get()=='':
            student_age_ent.config(highlightbackground='red',highlightcolor='red')
            student_age_ent.focus()
            message_box(message='Student Age is Required')
        elif student_contact_ent.get()=='':
            student_contact_ent.config(highlightbackground='red',highlightcolor='red')
            student_contact_ent.focus()
            message_box(message='Student Contact Number is\nRequired')
        elif select_class_btn.get()=='':
            select_class_btn.focus()
            message_box(message='Select Student Class is\nRequired')
        elif student_email_ent.get()=='':
            student_email_ent.config(highlightbackground='red',highlightcolor='red')
            student_email_ent.focus()
            message_box(message='Student Email is Required')
        elif not check_invalid_email(email=student_email_ent.get().lower()):
            student_email_ent.config(highlightbackground='red', highlightcolor='red')
            student_email_ent.focus()
            message_box(message='Invalid Email')


        elif account_password_ent.get()=='':
            account_password_ent.config(highlightbackground='red', highlightcolor='red')
            account_password_ent.focus()
            message_box(message='Account Password is Required')

        else:

            pic_data=b''

            if pic_path.get()!='':
                resize_pic=Image.open(pic_path.get()).resize((100,100))
                resize_pic.save('temp_pic.png')

                read_data=open('temp_pic.png','rb')
                pic_data=read_data.read()
                read_data.close()

            else:
                read_data = open('C:\\student_management_system\\Images\\add_image.png', 'rb')
                pic_data = read_data.read()
                read_data.close()
                pic_path.set('C:\\student_management_system\\Images\\add_image.png')

            add_data(id_number=student_id.get(),
                     password=account_password_ent.get(),
                     name=student_name_ent.get(),
                     age=student_age_ent.get(),
                     gender=student_gender.get(),
                     phone_number=student_contact_ent.get(),
                     student_class=select_class_btn.get(),
                     email=student_email_ent.get(),
                     pic_data=pic_data)



            data=f"""
{student_id.get()}
{student_name_ent.get()}
{student_gender.get()}
{student_age_ent.get()}
{select_class_btn.get()}
{student_contact_ent.get()}
{student_email_ent.get()}       
"""
            get_student_card=draw_student_card(student_pic_path=pic_path.get(),student_data=data)
            student_card_page(student_card_obj=get_student_card)
            add_account_page_fm.destroy()
            root.update()
            message_box("Account Created Successfully")



    add_account_page_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)

    add_pic_section_fm = tk.Frame(add_account_page_fm, highlightbackground=bg_color, highlightthickness=2)

    add_pic_btn = tk.Button(add_pic_section_fm, image=add_student_pic_icon, bd=0,command=open_pic)
    add_pic_btn.pack()

    add_pic_section_fm.place(x=5, y=5, width=105, height=105)

    student_name_lb = tk.Label(add_account_page_fm, text="Enter Student Name", font=('Bold', 12))
    student_name_lb.place(x=5, y=130)

    student_name_ent = tk.Entry(add_account_page_fm, font=('Bold', 15), highlightcolor=bg_color,
                                highlightbackground='gray', highlightthickness=2)
    student_name_ent.place(x=5, y=160, width=180)
    student_name_ent.bind('<KeyRelease>',lambda e: remove_highlight_warning(entry=student_name_ent))

    student_gender_lb = tk.Label(add_account_page_fm, text="Select Your Gender", font=('Bold', 12))
    student_gender_lb.place(x=5, y=210)


    male_gender_btn = tk.Radiobutton(add_account_page_fm, text='Male', font=('Bold', 12), variable=student_gender,
                                     value='male')
    male_gender_btn.place(x=5, y=235)

    female_gender_btn = tk.Radiobutton(add_account_page_fm, text='Female', font=('Bold', 12), variable=student_gender,
                                       value='female')
    female_gender_btn.place(x=75, y=235)

    student_gender.set('male')

    student_age_lb = tk.Label(add_account_page_fm, text="Enter Student Age", font=('Bold', 12))
    student_age_lb.place(x=5, y=275)

    student_age_ent = tk.Entry(add_account_page_fm, font=('Bold', 15), highlightcolor=bg_color,
                               highlightbackground='gray', highlightthickness=2)
    student_age_ent.place(x=5, y=305, width=180)
    student_age_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_age_ent))

    student_contact_lb = tk.Label(add_account_page_fm, text="Enter Student Contact Number", font=('Bold', 12))
    student_contact_lb.place(x=5, y=360)

    student_contact_ent = tk.Entry(add_account_page_fm, font=('Bold', 15), highlightcolor=bg_color,
                                   highlightbackground='gray', highlightthickness=2)
    student_contact_ent.place(x=5, y=390, width=180)
    student_contact_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_contact_ent))

    student_class_lb = tk.Label(add_account_page_fm, text="Select Student Class", font=('Bold', 12))
    student_class_lb.place(x=5, y=445)

    select_class_btn = Combobox(add_account_page_fm, font=('Bold', 15), state='readonly', values=class_list)
    select_class_btn.place(x=5, y=475, width=180, height=30)

    student_id_lb = tk.Label(add_account_page_fm, text='Student ID Number:', font=('Bold', 12))
    student_id_lb.place(x=240, y=35)

    student_id = tk.Entry(add_account_page_fm, font=('Bold', 18), bd=0, )
    student_id.place(x=380, y=35, width=80)

    student_id.insert(tk.END, '123456')
    student_id.config(state='readonly')

    generate_id_number()

    id_info_lb = tk.Label(add_account_page_fm, text="""Automatically Generated ID Number
! Remember Using This ID Number
Student will Login Account""", justify=tk.LEFT)
    id_info_lb.place(x=240, y=65)

    student_email_lb = tk.Label(add_account_page_fm, text="Enter Student Email ID", font=('Bold', 12))
    student_email_lb.place(x=240, y=130)

    student_email_ent = tk.Entry(add_account_page_fm, font=('Bold', 15), highlightcolor=bg_color,
                                 highlightbackground='gray', highlightthickness=2)
    student_email_ent.place(x=240, y=160, width=180)
    student_email_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_email_ent))

    email_info_lb = tk.Label(add_account_page_fm, text="""Via Email ID Student
Can Recover Account
! In Case Forgetting Password And Also
Student will get Future Notifications.""", justify=tk.LEFT)
    email_info_lb.place(x=240, y=200)

    account_password_lb = tk.Label(add_account_page_fm, text="Create Account Password", font=('Bold', 12))
    account_password_lb.place(x=240, y=275)

    account_password_ent = tk.Entry(add_account_page_fm, font=('Bold', 15), highlightcolor=bg_color,
                                    highlightbackground='gray', highlightthickness=2)
    account_password_ent.place(x=240, y=307, width=180)
    account_password_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=account_password_ent))

    account_password_info_lb = tk.Label(add_account_page_fm, text="""Via Student Created Password
And Provided Student ID Number
Student Can Login Account.""", justify=tk.LEFT)
    account_password_info_lb.place(x=240, y=345)

    home_btn = tk.Button(add_account_page_fm, text='Home', font=('Bold', 15), bg='red', fg='white', bd=0,
                         command=forward_to_welcome_page)
    home_btn.place(x=240, y=420)

    submit_btn = tk.Button(add_account_page_fm, text='Submit', font=('Bold', 15), bg=bg_color, fg='white', bd=0,command=check_input_validation)
    submit_btn.place(x=360, y=420)

    add_account_page_fm.pack(pady=5)
    add_account_page_fm.propagate(False)
    add_account_page_fm.config(width=480, height=580)


#starts from welcome page
if __name__ == "__main__":
    init_database()
    welcome_page()  # Start with the welcome page instead


    root.mainloop()
