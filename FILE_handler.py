from colour import Color
from matplotlib import pyplot as plt
from typing import Iterable
import re
import numpy as np
from PALETTE_handler import * 
import os
from shutil import copytree
from tqdm import tqdm

def plot_colors(colors : Iterable, title = "") : 
    fig, ax = plt.subplots()
    for i, color in enumerate(colors) : 
        if type(color) is tuple and max(color) > 1 : 
            color = color[0] / 255, color[1] / 255, color[2] / 255
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
    ax.set_xlim(0, len(colors))
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_aspect('equal')
    ax.set_title(title)
    plt.show()
    
class Color_Parser_FILE : 
    
    def __init__(self, file_path : str) :
        
        self.lines : list = open(file_path, "r").read().split("\n")
        self.colors = []
        
    def is_color(self, color_str : str) :
        if color_str == "" : 
            return False
        
        try : 
            Color(color_str)
            return True
        
        except :
            
            return False
    
    def select_rgba_tuple(self, line, index_rgba) : 
        end = line.find(")", index_rgba)
        begin = line.find("(", index_rgba)
        return line[begin:end + 1]
    
    def get_rgb_color_line(self, line : str) :
         
        line = line.replace(";", " ")   # FOR CSS DOCUMENTS
        line = line.replace("!", " ")  # FOR CSS DOCUMENTS
        line = line.replace("!", " ")  # FOR CSS DOCUMENTS
        
        line = line.replace("\"", " ")  # FOR JSON DOCUMENTS
        
        for m in re.finditer('rgb', line) : 
            
            self.colors.append(self.select_rgba_tuple(line, m.end()))
        
    def get_colors_line(self, line : str) : 
        
        line = line.replace(";", " ")
        line = line.replace("!", " ")
        line = line.replace(":", " ")
        
        line = line.replace("\"", " ")  # FOR JSON DOCUMENTS

        return [color for color in line.split(" ") if self.is_color(color)]
    
    def parse(self) :
        
        for line in self.lines :
            # self.get_rgb_color_line(line)
            if self.get_colors_line(line) != ['']: 
                self.colors += self.get_colors_line(line)
        
        self.colors = [color for color in self.colors if color != '']   
    def get_colors(self) : 
        self.parse()
        return self.colors
    
    
class Color_Analyzer_from_FILE : 
        
    def __init__(self, colors : Iterable) : 
        self.colors = {}
        self.colors["raw"] = colors
        self.original_colors = colors.copy()
        
    def plot(self) : 
        self.convert_to_rgb()
        plot_colors(self.colors['rgb'])
        
    def convert_to_rgb(self) : 
        rgb_list = []
        
        for k in range(len(self.colors['raw'])) : 
    
            if self.original_colors[k].startswith("(") : 
                self.colors['raw'][k] = eval(self.original_colors[k])
        for k in range(len(self.colors['raw'])) : 
            
            if not type(self.colors['raw'][k]) is tuple : 
                
                rgb_list.append(Color.get_rgb(Color(self.colors['raw'][k])))
            else : 
                rgb_list.append(Color.get_rgb(Color(rgb =  np.array(self.colors['raw'][k])[:3]/255)))

        self.colors['rgb'] = rgb_list
        
    def convert_to_hex(self) :
        hex_list = []
        
        for k in range(len(self.colors['raw'])) : 
            hex_list.append(Color.get_hex(Color(self.colors['raw'][k])))
            
        return  hex_list
        
    def rgb_to_hsl(self, rgb) :
        return Color.get_hsl(Color(rgb = rgb))
    
    def convert_to_hsl(self) : 
        if 'rgb' not in self.colors.keys() : self.convert_to_rgb()
        
        hsl_list = []
        for k in range(len(self.colors['raw'])) : 
            
           hsl_list.append(self.rgb_to_hsl(self.colors['rgb'][k]))
           
        self.colors['hsl'] = hsl_list
        
    def rgb_to_cvt(self, rgb : tuple) -> tuple:
        """
        rgb_to_cvt PARTIAL CVT IMPLEMENTATION

        Parameters
        ----------
        rgb : tuple
            rbg tuple to convert to cvt

        Returns
        -------
        tuple
            partially converted cvt tuple
        """        
        cvt_matrix = [[0.412453, 0.357580, 0.180423],
                      [0.2126771, 0.715160, 0.072169], 
                      [0.019334, 0.119193, 0.950227]]
        return tuple(np.dot(cvt_matrix, np.array(rgb)))
        
    # TODO: FULL CVT IMPLEMENTATION WITH a*,b* and u*,v* space

        
    def convert_to_cvt(self) : 
   
        if 'rgb' not in self.colors.keys() : self.convert_to_rgb()
        
        cvt_list = []   
        for k in range(len(self.colors['rgb'])) : 
            cvt_list.append(self.rgb_to_cvt(self.colors['rgb'][k]))
            
        self.colors['cvt'] = cvt_list
        
    
    # TODO: implement other distanance metrics
    
    def compute_all_spaces(self) :
        if 'rgb' not in self.colors.keys() : self.convert_to_rgb()
        self.convert_to_hsl()
        self.convert_to_cvt()
        
    def match_palette(self, palette : PalletteHandler) -> dict:
        """
        match_palette MATCHES A PALETTE TO THE COLORS, palette must be introduce in RGB format

        Parameters
        ----------
        palette : Iterable
            palette to match

        Returns
        -------
        Iterable
            matches between the palette and the colors
        """        
        palette.compute_all_spaces()
        self.compute_all_spaces()
        closest_colors = {}
        
        for key in palette.colors.keys() : 
            if key == 'raw' : 
                pass
            else : 
                palette_closer = []
                
                for color in self.colors[key] : 
                    
                    palette_closer.append(palette.get_closest_color(color, space = key))
                    
                closest_colors[key] = palette_closer
        return closest_colors
    
    def plot_palette_match(self, palette : PalletteHandler) : 
        matches = self.match_palette(palette)
        for key in matches.keys() : 
            
            plot_colors(np.array(palette.colors['rgb'])[matches[key]], title = key + " matched")
            plot_colors(self.colors['rgb'], title= key + " original")
    
    #TODO: Variation are not possile yet, the matching is only based on the best match
    
    def vote_for_palette(self, palette : PalletteHandler) : 
        matches = self.match_palette(palette)
        votes = {}
        
        for k in range(len(self.colors['raw'])) : 
            votes[k] = [matches[key][k] for key in matches.keys()]
            
        for key in votes.keys() : 
            votes[key] = max(votes[key], key = votes[key].count)
            
        return votes

    def plot_final_match(self, palette : PalletteHandler) : 
        final_match = self.vote_for_palette(palette)
        plot_colors(np.array(palette.colors['rgb'])[list(final_match.values())], title = " matched from Palette")
        plot_colors(self.colors['rgb'], title= " original")
    
        
def re_writer(file_path : str, palette : PalletteHandler, replace = False) :
    cp = Color_Parser_FILE(file_path)
    ca = Color_Analyzer_from_FILE(cp.get_colors())
    # print("SUCESS : File {} parsed".format(file_path))
    
    final_match = ca.vote_for_palette(palette)
    palette.final_colors = palette.colors['raw'].copy()
    if replace : 
        copy_file = open(file_path, "r").read()

        for k in range(len(ca.colors['raw'])) :
            index_palette = final_match[k]
            
            if type(ca.colors['raw'][k]) is tuple : 

                value_replacement = str(tuple([int(255 * k) for k in palette.colors['rgb'][index_palette]] + [eval(ca.original_colors[k])[-1]]))
                copy_file = copy_file.replace(ca.original_colors[k], value_replacement)
            else :
                copy_file = copy_file.replace(ca.original_colors[k], palette.final_colors[index_palette])
                
        with open(file_path, "w") as file : 
            file.write(copy_file)
        
        # print("SUCESS : File saved as " + file_path + "\n using the given palette")
        
    else :  
        
        new_file_path = '.'.join(file_path.split(".")[:-1]) + "_new_palette." + file_path.split(".")[-1]
        
        copy_file = open(file_path, "r").read()
                
        for k in range(len(ca.colors['raw'])) :
            index_palette = final_match[k]
            
            if type(ca.colors['raw'][k]) is tuple : 

                value_replacement = str(tuple([int(255 * k) for k in palette.colors['rgb'][index_palette]] + [eval(ca.original_colors[k])[-1]]))
                copy_file = copy_file.replace(ca.original_colors[k], value_replacement)
            else :
                copy_file = copy_file.replace(ca.original_colors[k], palette.final_colors[index_palette])
                
        with open(new_file_path, "w") as file : 
            
            file.write(copy_file)

        # print("SUCESS : File saved as " + new_file_path + "\n using the given palette")

class FileWriter : 
    
    def __init__(self) : 
        pass
    
    def re_write(self, file_path : str, palette : PalletteHandler, replace = False) :
        
        cp = Color_Parser_FILE(file_path)
        ca = Color_Analyzer_from_FILE(cp.get_colors())
        # print("SUCESS : File {} parsed".format(file_path))
        
        final_match = ca.vote_for_palette(palette)
        palette.final_colors = palette.colors['raw'].copy()
        if replace : 
            copy_file = open(file_path, "r").read()
    
            for k in range(len(ca.colors['raw'])) :
                index_palette = final_match[k]
                
                if type(ca.colors['raw'][k]) is tuple : 
    
                    value_replacement = str(tuple([int(255 * k) for k in palette.colors['rgb'][index_palette]] + [eval(ca.original_colors[k])[-1]]))
                    copy_file = copy_file.replace(ca.original_colors[k], value_replacement)
                else :
                    copy_file = copy_file.replace(ca.original_colors[k], palette.final_colors[index_palette])
                    
            with open(file_path, "w") as file : 
                file.write(copy_file)
            
            # print("SUCESS : File saved as " + file_path + "\n using the given palette")
            
        else :  
            
            new_file_path = '.'.join(file_path.split(".")[:-1]) + "_new_palette." + file_path.split(".")[-1]
            
            copy_file = open(file_path, "r").read()
                    
            for k in range(len(ca.colors['raw'])) :
                index_palette = final_match[k]
                
                if type(ca.colors['raw'][k]) is tuple : 
    
                    value_replacement = str(tuple([int(255 * k) for k in palette.colors['rgb'][index_palette]] + [eval(ca.original_colors[k])[-1]]))
                    copy_file = copy_file.replace(ca.original_colors[k], value_replacement)
                else :
                    copy_file = copy_file.replace(ca.original_colors[k], palette.final_colors[index_palette])
                    
            with open(new_file_path, "w") as file : 
                
                file.write(copy_file)
    
            # print("SUCESS : File saved as " + new_file_path + "\n using the given palette"
        self.palette = palette.colors
        
    def match_file_from_image(self, file_path : str, path_image : str) :
        print('Creating the palette from the image...')
        palette = PalletteHandler()
        palette.set_palette_from_image(path_image)
        
        self.re_write(file_path, palette, replace = True)
    
    def match_file_from_palette(self, file_path : str, palette : Iterable) :
        
        ph = PalletteHandler()
        ph.set_palette_from_colors(palette)
        
        self.re_write(file_path, ph, replace = True)
    
    def match_dir_tree_from_image(self, dir_path : str, path_image : str, replace = False, replace_directory = False, extensions = ["css", "json", "html", "txt", 'svg']) :
        print('Creating the palette from the image...')

        ph = PalletteHandler()
        ph.set_palette_from_image(path_image)
        
        print('Matching the directory tree with the color palette...')
        if replace : 
            for file in  tqdm([os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(dir_path)) for f in fn]) :
                if file.split(".")[-1] in extensions : 
                    self.re_write(file, ph, replace = True)
        else :
            
            if not replace_directory : raise ValueError("you must precise the desired replace directory if replace is False, you don't have to create this directory")
            
            else : 
                copytree(dir_path, replace_directory)
                
                for file in  [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(replace_directory)) for f in fn] :
                    if file.split(".")[-1] in extensions : 
                        self.re_write(file, ph, replace = True)
      
                        
    def match_dir_tree_from_palette(self, dir_path : str, palette : Iterable, replace = False, replace_directory = False, extensions = ["css", "json", "html", "txt", 'svg']) :
        
        ph = PalletteHandler()
        ph.set_palette_from_colors(palette)
        
        if replace : 
            for file in  [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(dir_path)) for f in fn] :
                if file.split(".")[-1] in extensions : 
                    self.re_write(file, ph, replace = True)
        else :
            
            if not replace_directory : raise ValueError("you must precise the desired replace directory if replace is False, you don't have to create this directory")
            
            else : 
                copytree(dir_path, replace_directory)
                
                for file in tqdm([os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(replace_directory)) for f in fn]) :
                    if file.split(".")[-1] in extensions : 
                        self.re_write(file, ph, replace = True)
                