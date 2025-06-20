from abc import ABC, abstractmethod

from controller.controller import Controller
from controller.controller_inputs import ControllerInput
from display.display import Display
from themes.theme import Theme
from views.selection import Selection
from views.view import View


class ListView(View):
    def __init__(self):
        super().__init__()
        self.current_top = 0
        self.current_bottom = 0
        self.clear_display_each_render_cycle = True
        self.include_index_text = True

    def center_selection(self):
        if(self.selected != 0):
            window_size = self.current_bottom - self.current_top
            half_window = window_size // 2

            # Try to center selected
            new_top = self.selected - half_window
            new_bottom = new_top + window_size

            # Clamp top and bottom
            if new_top < 0:
                new_top = 0
                new_bottom = window_size
            if new_bottom > len(self.options):
                new_bottom = len(self.options)
                new_top = new_bottom - window_size

            self.current_top = new_top
            self.current_bottom = new_bottom

    @abstractmethod
    def _render(self):
        pass

    def get_selected_option(self):
        if 0 <= self.selected < len(self.options):
            return self.options[self.selected]
        else:
            return None

    def selection_made(self):
        #Override as needed
        pass

    def get_selection(self, select_controller_inputs = [ControllerInput.A]):
        self._render_common()
        
        if(Controller.get_input()):
            if Controller.last_input() == ControllerInput.DPAD_UP:
                self.adjust_selected(-1)
            elif Controller.last_input() == ControllerInput.DPAD_DOWN:
                self.adjust_selected(1)
            elif Controller.last_input() in select_controller_inputs: #requested inputs have priority over the rest
                self.selection_made()
                return Selection(self.get_selected_option(),Controller.last_input(), self.selected)
            elif Controller.last_input() == ControllerInput.L1:
                if(Theme.skip_main_menu()):
                    return Selection(self.get_selected_option(),Controller.last_input(), self.selected)
                else:
                    self.adjust_selected(-1*self.max_rows+1)
            elif Controller.last_input() == ControllerInput.R1:
                if(Theme.skip_main_menu()):
                    return Selection(self.get_selected_option(),Controller.last_input(), self.selected)
                else:
                    self.adjust_selected(self.max_rows-1)
            elif Controller.last_input() == ControllerInput.B:
                self.selection_made()
                return Selection(self.get_selected_option(),Controller.last_input(), self.selected)

            self._render_common()


        return Selection(self.get_selected_option(), None, self.selected)
    
    def _render_common(self):
        #if(self.clear_display_each_render_cycle):
        Display.clear(self.top_bar_text)
        
        self.adjust_selected_top_bottom_for_overflow()

        self._render()
        if(self.include_index_text):
            Display.add_index_text(self.selected+1, len(self.options), force_include_index = True, 
                                   letter=self.options[self.selected].get_primary_text()[0])
        Display.present()

    def adjust_selected_top_bottom_for_overflow(self):
        self.selected = max(0, self.selected)
        self.selected = min(len(self.options)-1, self.selected)
        
        while(self.selected < self.current_top):
            self.current_top -= 1
            self.current_bottom -=1

        while(self.selected >= self.current_bottom):
            self.current_top += 1
            self.current_bottom +=1


    def adjust_selected(self, amount):
        #print(f"Adjust by {amount}")
        #print(f"    selected = {self.selected}, current_top = {self.current_top}, current_bottom = {self.current_bottom}")
        if(self.selected == 0 and amount < 0):
            # Hitting up when on the top most row
            #print(f"    Wrapping from top to bottom")
            delta = self.current_bottom - self.current_top
            self.selected = len(self.options)-1
            self.current_bottom = len(self.options)
            self.current_top = max(0, self.current_bottom - delta)
        elif(self.selected == len(self.options)-1 and amount > 0):
            # Hitting down when on the bottom most row
            #print(f"    Wrapping from bottom to top")
            delta = self.current_bottom - self.current_top
            self.selected = 0
            self.current_top = 0
            #print(f"    delta = {delta}, len(self.options) = {len(self.options)}")
            self.current_bottom = min(delta, len(self.options))
        else :    
            # Normal adjustment
            #print(f"    Normal Adjustment")
            self.selected += amount
            if(amount > 1):
                self.current_top += amount
                self.current_bottom += amount