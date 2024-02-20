import argparse
from tools.FILE_handler import *
import os 
from typing import Iterable
from shutil import copyfile

def main():
    
    FW = FileWriter()
    
    parser = argparse.ArgumentParser(description='This script is used for parsing files, analyzing color data, and replacing color palettes. It can use a given palette or create a palette from an image. For better understanding of the project please refer to the git page : ')
    parser.add_argument('--path', type=str, required=True, help='The directory or file path to process')
    parser.add_argument('--replace_path', type=str, required=False, help='The directory to replace')
    parser.add_argument('--extensions', type=str, nargs='+', required=False, help='The file extensions to process', default= ["css", "json", "html", "txt", 'svg'])
    parser.add_argument('--palette', type = Iterable, required=False, help='The palette to use for the file', default = None)
    parser.add_argument('--image', type = str, required=False, help='The path to image to use for the palette', default = None)
    
    if parser.parse_args().palette != None and parser.parse_args().palette_image != None : 
        raise ValueError("You cannot specify both a palette and a palette image")
    
    if parser.parse_args().palette != None and parser.parse_args().palette_image != None : 
        raise ValueError("You must specify either a palette or a palette image")
    
    if not os.path.exists(parser.parse_args().path) :
        raise ValueError("The file or directory path does not exist")
    
    if os.path.isdir(parser.parse_args().path) : 
        
        if parser.parse_args().palette != None : 
            
            if parser.parse_args().replace_path == None :
                FW.match_dir_tree_from_palette(dir_path=parser.parse_args().path, palette = parser.parse_args().palette, replace = True, extensions=parser.parse_args().extensions)
            else :
                FW.match_dir_tree_from_palette(dir_path=parser.parse_args().path, palette = parser.parse_args().palette, replace = False, replace_directory=parser.parse_args().replace_path, extensions=parser.parse_args().extensions)
       
        if parser.parse_args().image != None : 
            
            if parser.parse_args().replace_path == None :
                FW.match_dir_tree_from_image(dir_path=parser.parse_args().path, path_image= parser.parse_args().image, replace = True, extensions=parser.parse_args().extensions)
            else :
                FW.match_dir_tree_from_image(dir_path=parser.parse_args().path, path_image = parser.parse_args().image, replace = False, replace_directory=parser.parse_args().replace_path, extensions=parser.parse_args().extensions)
    
    else : 
        
        if parser.parse_args().palette != None : 
            
            if parser.parse_args().replace_path == None :
                FW.match_file_from_palette(file_path=parser.parse_args().path, palette = parser.parse_args().palette)
            else :
                copyfile(parser.parse_args().path, parser.parse_args().replace_path)
                FW.match_file_from_palette(file_path=parser.parse_args().replace_path, palette = parser.parse_args().palette)
       
        if parser.parse_args().image != None : 
            
            if parser.parse_args().replace_path == None :
                FW.match_file_from_image(file_path=parser.parse_args().path, palette = parser.parse_args().palette)
            else :
                copyfile(parser.parse_args().path, parser.parse_args().replace_path)
                FW.match_file_from_image(file_path=parser.parse_args().replace_path, path_image = parser.parse_args().image)
       
if __name__ == "__main__":
    main()