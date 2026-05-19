import tkinter as tk
from horror_asset_gen.tools.gui import HorrorAssetGenGUI

def main():
    root = tk.Tk()
    app = HorrorAssetGenGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
