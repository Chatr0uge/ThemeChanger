from colour import Color
from matplotlib import pyplot as plt
from typing import Iterable
import numpy as np
from PIL import Image
from sklearn.cluster import BisectingKMeans

class PalletteHandler : 
    
    def __init__(self) : 
        self.colors = {'raw' : [], 'rgb' : [], 'hsl' : [], 'cvt' : []}
        
    def set_palette_from_colors(self, palette : Iterable ) :
        
        self.colors['raw'] = palette
    
    def set_palette_from_image(self, image_path : str, number_of_colors : int = 10) :
        
        img = Image.open(image_path)
        img_data = np.array(img)
        
        km = BisectingKMeans(n_clusters = number_of_colors)
        km.fit(img_data.reshape(-1, 3).astype(np.float16))
        
        self.colors['raw'] = [Color(rgb = (km.cluster_centers_[k] / 255)).hex for k in range(number_of_colors)]
        
    def plot_colors(self, ax = False) : 
        if ax : 
            for i, color in enumerate(self.colors['raw']) : 
                if type(color) is tuple and max(color) > 1 : 
                    color = color[0] / 255, color[1] / 255, color[2] / 255
                ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
            ax.set_xlim(0, len(self.colors['raw']))
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_aspect('equal')
        else : 
            fig, ax = plt.subplots()
            for i, color in enumerate(self.colors['raw']) : 
                if type(color) is tuple and max(color) > 1 : 
                    color = color[0] / 255, color[1] / 255, color[2] / 255
                ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
            ax.set_xlim(0, len(self.colors['raw']))
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_aspect('equal')
            plt.show()
    
    def convert_hex_to_rgb(self, color : str) : 
    
        return Color(color).rgb

    def convert_to_rgb(self) : 
        
        self.colors['rgb'] = [self.convert_hex_to_rgb(color) for color in self.colors['raw'] if not type(color) is tuple]
    
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

    def convert_to_cvt(self) : 
   
        self.convert_to_rgb()
        
        cvt_list = []   
        for k in range(len(self.colors['rgb'])) : 
            cvt_list.append(self.rgb_to_cvt(self.colors['rgb'][k]))
            
        self.colors['cvt'] = cvt_list
    
    def compute_all_spaces(self) :
        self.convert_to_rgb()
        self.convert_to_hsl()
        self.convert_to_cvt()
    
    def euclidean_distance(self, color1, color2) : 
        return np.linalg.norm(np.array(color1) - np.array(color2), ord = 2)
    
    def get_closest_color(self, color, space) : 
        return np.argmin(list(map(lambda x : self.euclidean_distance(color, x), self.colors[space])))
    
    