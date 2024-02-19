from colour import Color
from matplotlib import pyplot as plt
from typing import Iterable
import re
import numpy as np
from tools.PALETTE_handler import * 

def plot_colors(colors : Iterable, title = "", ax = False) : 
    if not ax : 
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
    else :
        for i, color in enumerate(colors) : 
            if type(color) is tuple and max(color) > 1 : 
                color = color[0] / 255, color[1] / 255, color[2] / 255
            ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
        ax.set_xlim(0, len(colors))
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_aspect('equal')
        ax.set_title(title)
    
    
class Color_Analyzer_from_IMAGE : 
        
    def __init__(self, image_path : str) : 

        self.img_data = np.array(Image.open(image_path))
        if self.img_data.shape[2] == 4 : self.img_data = self.img_data[:,:,:3]
        self.colors = {'raw' : [], 'rgb' : [], 'hsl' : [], 'cvt' : []}
    
    def plot(self) : 
        self.convert_to_rgb()
        plot_colors(self.colors['rgb'])
        
    def convert_to_rgb(self) : 
        rgb_list = []
        for k in range(len(self.colors['raw'])) : 
            
            if not type(self.colors['raw'][k]) is tuple : 
                
                rgb_list.append(Color.get_rgb(Color(self.colors['raw'][k])))
            else : 
                rgb_list.append(Color.get_rgb(Color(rgb =  np.array(self.colors['raw'][k])/255)))

        self.colors['rgb'] = rgb_list
        
    def convert_to_hex(self) :
        hex_list = []
        
        for k in range(len(self.colors['raw'])) : 
            hex_list.append(Color.get_hex(Color(self.colors['raw'][k])))
            
        return  hex_list
        
    def rgb_to_hsl(self, rgb) :
        return Color.get_hsl(Color(rgb = rgb))
    
    def convert_to_hsl(self) : 
        self.convert_to_rgb()
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
   
        self.convert_to_rgb()
        
        cvt_list = []   
        for k in range(len(self.colors['rgb'])) : 
            cvt_list.append(self.rgb_to_cvt(self.colors['rgb'][k]))
            
        self.colors['cvt'] = cvt_list
        
    
    # TODO: implement other distanance metrics
    
    def compute_all_spaces(self) :
        self.convert_to_rgb()
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
    
    def set_palette_on_image(self,  palette : PalletteHandler, number_of_colors : int = 10, plot = True) : 
        
        km = BisectingKMeans(n_clusters = number_of_colors)
        km.fit(self.img_data.reshape(-1, 3).astype(np.float16))
        
        self.colors['raw'] = [tuple(km.cluster_centers_[k]) for k in range(number_of_colors)]
        final_match = self.vote_for_palette(palette)
        self.colors_match = np.array([palette.colors['rgb'][k] for k in final_match.values()])
        
        if plot : 
            fig, ax  = plt.subplots(2, height_ratios = [0.1, 1])
            plot_colors(self.colors_match, title = " matched from Palette", ax = ax[0])
            ax[1].imshow(self.colors_match[km.labels_].reshape(self.img_data.shape))
            ax[1].axis('off')
            plt.show()
            
        return self.colors_match[km.labels_].reshape(self.img_data.shape)
     