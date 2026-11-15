"""Image Generator

This script is a modified version of the tkinter_ui.py script provided in the min_dalle repository.
The script loads a tkinter Image Generator gui for the user to interact with.
The user is able to provide a prompt that will be generated.
The user can also tweak the supercondition factor to generate better results
The user can generate images, save images, or quit using the buttons on the GUI


Author:
    Armaan Ballagan - 26.6.2023
"""


from min_dalle_module.min_dalle import MinDalle
from IPython.display import display
import tkinter
from tkinter import ttk
import PIL
import PIL.Image
import PIL.ImageTk
import sys




def regen_root():
    """Creates the frame for the GUI"""
    global root
    global blank_image
    global padding_image

    root = tkinter.Tk()
    root.wm_resizable(False, False)

    blank_image = PIL.ImageTk.PhotoImage(PIL.Image.new(size=(256 * 2, 256 * 2), mode="RGB"))
    padding_image = PIL.ImageTk.PhotoImage(PIL.Image.new(size=(16, 16), mode="RGBA"))


model = MinDalle(
    models_root="./pretrained",
    is_mega=False, # my pc can't run mega :(
    is_reusable=True,
    is_verbose=True
)

regen_root()

print("launched other gui????")
label_image_content = blank_image

sv_prompt = tkinter.StringVar(value="artificial intelligence")
sv_temperature = tkinter.StringVar(value="1") #The largest logit is subtracted from the logits to avoid infs.  The logits are then divided by the `temperature`
sv_topk = tkinter.StringVar(value="128") #most probable tokens. I think this encodes the text so that it can be converted by adding noise
sv_supercond = tkinter.StringVar(value="16") #result in better agreement with the text but a narrower variety of generated images
bv_seamless = tkinter.BooleanVar(value=True) # made in token space not pixel space?

def generate():
    """generates an image based on user input using the min_dalle program"""
    # check fields
    try:
        temperature = float(sv_temperature.get())
    except:
        sv_temperature.set("ERROR")
        return
    try:
        topk = int(sv_topk.get())
    except:
        sv_topk.set("ERROR")
        return
    try:
        supercond = int(sv_supercond.get())
    except:
        sv_supercond.set("ERROR")
        return
    try:
        is_seamless = bool(bv_seamless.get())
    except:
        return
    # and continue

    global label_image_content
    image_stream = model.generate_image_stream(
        sv_prompt.get(),
        grid_size=1,
        seed=-1,
        progressive_outputs=True,
        is_seamless=is_seamless,
        temperature=temperature,
        top_k=topk,
        supercondition_factor=supercond,
        is_verbose=True
    )

    for image in image_stream:
        global final_image
        final_image = image
        label_image_content = PIL.ImageTk.PhotoImage(image)
        label_image.configure(image=label_image_content)
        label_image.update()
    

def save():
    """Exports generated images as generated Image.png under the folder 'Images'"""
    final_image.save('Images\generated Image.png')
    tkinter.Label(root, text="Image Saved!", font="arial 15").grid(column=0, row=11) #display "Image Saved" after Generation


frm = ttk.Frame(root, padding=16)
frm.grid()

props = ttk.Frame(frm)

# outer structure (hbox)
label_image = ttk.Label(frm, image=blank_image)
label_image.grid(column=0, row=0)
ttk.Label(frm, image=padding_image).grid(column=1, row=0)
props.grid(column=2, row=0)

# inner structure (properties and shit)
# prompt field
ttk.Label(props, text="Prompt:").grid(column=0, row=0)
ttk.Entry(props, textvariable=sv_prompt).grid(column=1, row=0)
ttk.Label(props, image=padding_image).grid(column=0, row=1)
ttk.Label(props, image=padding_image).grid(column=0, row=3)
ttk.Label(props, image=padding_image).grid(column=0, row=5)
# superconditioning field
ttk.Label(props, text="Supercondition Factor:").grid(column=0, row=6)
ttk.Entry(props, textvariable=sv_supercond).grid(column=1, row=6)
#label
ttk.Label(props, text= "Play around with this number to get desired results").grid(column=0, row=7) #Higher Number = Better Agreement with Prompt
ttk.Label(props, image=padding_image).grid(column=0, row=9)
# buttons
ttk.Button(props, text="Generate", command=generate).grid(column=0, row=10)
ttk.Button(props, text="Use Image", command=save).grid(column=1, row=10)
ttk.Button(props, text="Quit", command=root.destroy).grid(column=2, row=10)


root.mainloop()