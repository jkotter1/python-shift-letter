def loadStyleSheet():
    StylesheetString = """
            QLabel, QDateEdit, QComboBox, QCheckBox, QPushButton { 
                font-size: 15px
            } 

            QTextEdit { 
                 border: 1px solid; 
                 border-color: palette(mid); 
                 border-radius:5px; 
                 background-color: palette(base);
                 font-size: 15px
            }

            QTextEdit[readOnly=\"true\"] { 
                 color: palette(shadow);
            }

             QScrollBar:vertical {
                 border: 1px solid; 
                 border-color: palette(mid);
                 width: 15px;
                 margin: 16px 0 17px 0;
                 background: palette(button);
             }

             QScrollBar::handle:vertical {
                 background: palette(base);
                 border-top: 1px solid; 
                 border-bottom: 1px solid; 
                 border-color: palette(mid);
                 min-height: 10px;
             }

             QScrollBar::handle:vertical:hover {
                 background: palette(midlight);
             }

             QScrollBar::handle:vertical:pressed {
                 background: palette(dark);
             }

             QScrollBar::add-line:vertical {
             
                 border: 1px solid;
                 border-color: palette(mid);
                 height: 15px;
                 subcontrol-position: bottom;
                 subcontrol-origin: margin;
                 border-bottom-left-radius: 5px;
                 border-bottom-right-radius: 5px;
                 background: palette(base);
             }

             QScrollBar::sub-line:vertical {
                 border: 1px solid; 
                 border-color: palette(mid);
                 height: 15px;
                 subcontrol-position: top;
                 subcontrol-origin: margin;
                 border-top-left-radius: 5px;
                 border-top-right-radius: 5px;
                 background: palette(base);
             }

             QScrollBar::sub-line:vertical:hover {
                 background: palette(midlight);
             }

             QScrollBar::add-line:vertical:hover {
                 background: palette(midlight);
             }

             QScrollBar::sub-line:vertical::pressed {
                 background: palette(dark);
             }

             QScrollBar::add-line:vertical:pressed {
                 background: palette(dark);
             }

             QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                     background: none;} """

    return StylesheetString