from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from PIL import Image, ImageDraw, ImageChops, ImageFont

IP = "127.0.0.1"
SERVER_PORT = 3001
CLIENT_PORT = 9008

filename = "temp.txt"
imgname = "temp.png"
w, h = 128 , 64
img = Image.new("RGB", (w, h))
draw = ImageDraw.Draw(img)
mask = Image.new("L", img.size, 0)
masking = ImageDraw.Draw(mask)
background = Image.new("L", img.size, 0)
backdraw = ImageDraw.Draw(background)
output = img

font = ImageFont.truetype("/usr/share/fonts/TTF/FantasqueSansMono-Regular.ttf", 15)
in_menu = True
with open(filename, "r") as f:
    f_contents = f.read()
    tmp = f_contents.split()
    size = len(tmp)
    data = tmp[0:size:int(size/w)]

def sample_img():
    x0 = range(len(data))
    y0 = data
    for x1, y1 in zip(x0, y0):
        to_height = lambda n : h - ( (float(n)+1)*0.5 )*h
        y1 = to_height(y1)
        x2 = x1+1
        y2 = to_height(data[:x2+1][-1])
        
        start = (x1, y1)
        end = (x2, y2)
        draw.line([start, end], fill="white", width=0)

    
def pointers(start_pos=0, end_pos=w):
    if end_pos < start_pos:
        rec_a = ((start_pos, 0), (end_pos, h))
        
        masking.rectangle(((0, 0), img.size), fill="white")
        masking.rectangle(rec_a, fill="black", width=0)
        
        masking.text((0, 0),
                     "reverse",
                     font=font,
                     fill="black",
                     stroke_width=2,
                     stroke_fill="white")
        
    else:
        rec_a = ((start_pos, 0), (end_pos, h))
        
        masking.rectangle(((0, 0), img.size), fill="black")
        masking.rectangle(rec_a, fill="white", width=0)

        masking.text((0, 0),
                     "normal",
                     fill="white",
                     font=font,
                     stroke_width=2,
                     stroke_fill="black")
       
# def main():
#     if in_menu:
#         sample_img()
#         inv_img = ImageChops.invert(img)
#         pointers()
#         cmp = Image.composite(inv_img, img, mask)

#     else:

#         padx, pady = (8, 4)
#         octave = "a"
#         dmode = "d"
#         load = "xd"
#         save = "xq"
#         msg = [f"octave: {octave}",
#                f"dmode: {dmode}",
#                f"load: {load}",
#                f"save: {save}"]

#         for n in range(4):
#             draw.text((padx, pady+n*14), msg[n], font=font, fill="white")

#         cmp = img    
#     cmp.save("test.png")

# if (__name__ == "__main__"):
#     main()

def osc_handler(address, *args):
    if(address == "/main/pointers"):
        global output
        
        startpoint = args[0] * w
        endpoint = args[1] * w

        sample_img()
        inv_img = ImageChops.invert(img)
        pointers(startpoint, endpoint)
        
        process = Image.composite(inv_img, img, mask)
        # TODO display image SPI
        
        output = process
        #print(f"STARTPOINT: {startpoint}\nENDPOINT: {endpoint}\n")

    
    elif(address == "/main/menu"):
        padx, pady = (8, 4)
        mode = args[1]
        dur  = args[2]
        load = args[3]
        save = args[4]
        msg  = [f"mode: {mode}",
                f"dur:  {dur}",
                f"load: {load}",
                f"save: {save}"]

        backdraw.rectangle(((0, 0), img.size), fill="black")
        for n in range(4):
            backdraw.text((padx, pady+n*14), msg[n], font=font, fill="white")

        process = background
        # TODO display image SPI
        output = process
        #print(f"SELECTION: {args[0]}\nMODE: {args[1]}\nDURATION: {args[2]}\nSAVESLOT: {args[3]}\nLOADSLOT: {args[4]}\n")

    elif address == "/main/test": output.save(imgname)

    
def default_handler(address, *args):
    print(f"DEFAULT {address}: {args}")

dispatcher = Dispatcher()

dispatcher.map("/main*", osc_handler)
dispatcher.set_default_handler(default_handler)

server = BlockingOSCUDPServer((IP, SERVER_PORT), dispatcher)
server.serve_forever()  # Blocks forever
