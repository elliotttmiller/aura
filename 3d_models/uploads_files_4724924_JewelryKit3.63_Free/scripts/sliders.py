#! python 2

import rhinoscriptsyntax as rs
import Rhino
import Eto
import Eto.Drawing as drawing
import Eto.Forms as forms
import System
import math


class SliderGroup(forms.Panel):       
        
    def __init__(self):
        super(SliderGroup, self).__init__()
        
        self.DecimalPlaces = 2
        self.Handlers = []
        self.LabelWidth = 50
        self.Min = 0
        self.Max = 1
        self.SliderWidth = 200
        self.Text = "Label: "
        self.TextBoxWidth = 50
        self.TickPanel = None
        self.Value = 0.0        

        self.Padding = drawing.Padding(2)

        self.Label = self.CreateLabel()
        self.SliderPanel = self.CreateSliderPanel()
        self.TextBox = self.CreateTextBox()
        
        layout = forms.DynamicLayout()
        layout.DefaultSpacing = drawing.Size(5,5)
        layout.BeginVertical()
        layout.BeginHorizontal()
        layout.AddAutoSized(self.Label)
        layout.AddAutoSized(self.SliderPanel)
        layout.AddAutoSized(self.TextBox)
        layout.EndHorizontal()
        layout.EndVertical()
        self.Content = layout

    def CalculateSliderValue(self):
        slider_value = self.Value * (math.pow(10, self.DecimalPlaces))
        return slider_value

    def CalculateTrueValue(self):
        value = self.Slider.Value / (math.pow(10, self.DecimalPlaces))
        return value
        
    def CreateLabel(self):
        label = forms.Label()
        label.Text = self.Text
        label.Width = self.LabelWidth
        label.TextAlignment = forms.TextAlignment.Right
        return label

    def CreateSliderPanel(self):
        pnl = forms.Panel()
        pnl.Width = self.SliderWidth
        pnl.Height = 24

        slider = forms.Slider()
        slider.Width = self.SliderWidth
        slider.MaxValue = 10
        slider.TickFrequency = 0
        slider.ValueChanged += self.HandleSliderChanged
        self.Slider = slider

        self.TickPanel = self.CreateTickPanel()

        layout = Eto.Forms.PixelLayout()
        layout.Add(slider, 0, 0)
        layout.Add(self.TickPanel, 5, 20)

        pnl.Content = layout

        return pnl

    def CreateTextBox(self):
        tb = forms.TextBox()
        tb.Width = self.TextBoxWidth
        tb.TextAlignment = forms.TextAlignment.Right
        tb.GotFocus += self.HandleTextBoxGotFocus
        tb.LostFocus += self.HandleTextBoxLostFocus
        return tb

    def CreateTickPanel(self):
        tp = forms.Panel()
        tp.Height = 4
        tp.Width = self.SliderWidth - 10
        tp.BackgroundColor = Eto.Drawing.Colors.Transparent

        tick_count = 5
        ticks = []
        for i in range(tick_count):
            ticks.append(self.CreateTick())

        layout = forms.PixelLayout()
        sections = tick_count-1
        for i in range(tick_count):
            pos = int((i) * tp.Width/sections)

            if i > 0 and i < 3: pos -= 2
            if i >= 3: pos -= 1

            layout.Add(ticks[i], pos, 0)

        tp.Content = layout

        return tp

    def CreateTick(self):
        t = forms.Panel()
        t.Height = 4
        t.Width = 1
        t.BackgroundColor = Eto.Drawing.Color.FromArgb(169, 169, 169, 255)
        return t

    def Disable(self):
        self.Label.Enabled = False
        self.Slider.Enabled = False
        self.TextBox.Enabled = False
        self.TickPanel.Enabled = False

    def Enable(self):
        self.Label.Enabled = True
        self.Slider.Enabled = True
        self.TextBox.Enabled = True
        self.TickPanel.Enabled = True

    def HandleSliderChanged(self, sender, e):
        self.Value = self.CalculateTrueValue()
        self.Update()

    def HandleTextBoxGotFocus(self, sender, e):
        self.Slider.ValueChanged -= self.HandleSliderChanged
        self.TextBox.TextChanged += self.HandleTextBoxTextChanged
        self.TextBox.KeyUp += self.HandleTextBoxKeyUp

    def HandleTextBoxKeyUp(self, sender, e):
        if e.Key == forms.Keys.Enter:
            self.Update()

    def HandleTextBoxLostFocus(self, sender, e):
        self.TextBox.KeyUp -= self.HandleTextBoxKeyUp
        self.TextBox.TextChanged -= self.HandleTextBoxTextChanged
        self.Slider.ValueChanged += self.HandleSliderChanged
        self.Update()

    def HandleTextBoxTextChanged(self, sender, e):
        # initialize value
        value = 0

        # try to convert text to a value
        try:
            value = float(self.TextBox.Text)
            value = round(value, self.DecimalPlaces)
        except:
            pass

        # make sure we haven't gone past the limits
        if value < self.Min:value = self.Min
        if value > self.Max:value = self.Max 

        # set value and slider value
        # note: we can't use SetValue or Update as those interfere with typing
        self.Value = value
        self.Slider.Value = self.CalculateSliderValue()

        # notify subscribers
        self.NotifySubscribers()

    def IsEnabled(self):
        if self.Label.Enabled:
            return True
        else:
            return False        

    def NotifySubscribers(self):
        for h in self.Handlers:
            try:
                h(self)
            except Exception as e:
                Rhino.RhinoApp.WriteLine('Notify: ' + str(e))

    def SetMinMax(self, minimum, maximum):
        self.Min = minimum
        self.Max = maximum
        self.SetDecimalPlaces(self.DecimalPlaces)

    def SetDecimalPlaces(self, decimal_places):
        if decimal_places < 0: decimal_places = 0
        if decimal_places > 4: decimal_places = 4
        self.DecimalPlaces = decimal_places
        self.Slider.MaxValue = self.Max * math.pow(10, self.DecimalPlaces)
        self.Slider.MinValue = self.Min * math.pow(10, self.DecimalPlaces)
        # self.Slider.TickFrequency = round((self.Slider.MaxValue - self.Slider.MinValue)/5,0)
        self.Slider.Value = self.CalculateSliderValue()
        self.Update()
        
    def SetEnabled(self, enabled):
        self.Label.Enabled = enabled
        self.Slider.Enabled = enabled
        self.TextBox.Enabled = enabled
        self.TickPanel.Enabled = enabled

    def SetValue(self, value):
        self.Value = value
        self.Slider.Value = self.CalculateSliderValue()
        self.Update()

    def Subscribe(self, handler):
        if handler not in self.Handlers:
            self.Handlers.append(handler)

    def Unsubscribe(self, handler):
        if handler in self.Handlers:
            self.Handlers.remove(handler)

    def Update(self):
        str_value = ''
        format_str = '{0:.'+ str(self.DecimalPlaces) + 'f}'
        str_value = format_str.format(float(self.Value))
        self.TextBox.Text = str_value
        self.NotifySubscribers()

