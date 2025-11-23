# Slide Deck Creation Guide

## ✅ What's Been Created

I've created two comprehensive resources for your presentation:

### 1. **SLIDE_DECK_CONTENT.md**
- Detailed content for all 13 slides
- Design guidelines (colors, fonts, spacing)
- Asset requirements (screenshots, diagrams, icons)
- Presentation tips

### 2. **presentation.html**
- Ready-to-use HTML presentation
- All 13 slides professionally designed
- IBM watsonx branding and color scheme
- Can be exported to PDF directly

---

## 🎨 How to Create Your Slide Deck

### Option 1: Use the HTML Presentation (Fastest)

1. **Open the HTML file**:
   ```
   Open: submission/presentation.html in your browser
   ```

2. **Export to PDF**:
   - Press `Ctrl+P` (Windows) or `Cmd+P` (Mac)
   - Select "Save as PDF" as destination
   - Set margins to "None"
   - Enable "Background graphics"
   - Save as `presentation.pdf`

3. **Customize**:
   - Edit the HTML file to add your email, demo links
   - Replace placeholder text with actual URLs
   - Add screenshots if needed

### Option 2: Use PowerPoint/Google Slides

1. **Use SLIDE_DECK_CONTENT.md as your guide**
2. **Follow the design guidelines**:
   - **Colors**: IBM Blue (#0F62FE), Purple (#8A3FFC), Teal (#08BDBA)
   - **Fonts**: IBM Plex Sans (or similar clean sans-serif)
   - **Layout**: 16:9 aspect ratio (1920x1080)

3. **Create each slide** following the content structure
4. **Add visuals**:
   - Screenshots from your running application
   - Architecture diagrams from `docs/architecture.md`
   - Icons for features and metrics

---

## 📸 Screenshots You Need

### Priority Screenshots:

1. **Chat Interface** (for Slide 7):
   - Run: `streamlit run src/frontend/app.py`
   - Take screenshot of chat with agent interaction
   - Show: User input → Agent response

2. **Dashboard** (for Slide 7):
   - Navigate to Dashboard tab
   - Capture metrics and active sessions

3. **Audit Log** (for Slide 7):
   - Settings → Recent Audit Events
   - Show JSON audit trail

### How to Take Screenshots:
```bash
# Start the application
run_demo.bat

# Wait for it to load, then:
# - Windows: Win+Shift+S
# - Mac: Cmd+Shift+4
```

---

## 🎯 Checklist for Completion

- [ ] Open `presentation.html` in browser
- [ ] Review all 13 slides
- [ ] Update placeholder text:
  - [ ] Your email address (Slide 13)
  - [ ] Demo video link (Slide 7, 13)
  - [ ] Team name (Slide 1)
- [ ] Take screenshots:
  - [ ] Chat interface
  - [ ] Dashboard
  - [ ] Audit log
- [ ] Export to PDF:
  - [ ] File size < 10MB
  - [ ] All slides visible
  - [ ] Colors look good
- [ ] Review final PDF for:
  - [ ] Spelling/grammar
  - [ ] Consistent branding
  - [ ] Clear visuals
  - [ ] Readable fonts

---

## 🚀 Quick Export Instructions

### From HTML to PDF:

1. Open `submission/presentation.html` in **Google Chrome** (recommended)
2. Press `Ctrl+P` (or `Cmd+P`)
3. **Destination**: Save as PDF
4. **Layout**: Landscape
5. **Margins**: None
6. **Options**: 
   - ✅ Background graphics
   - ✅ Headers and footers (optional)
7. Click **Save**
8. Name it: `Smart_Procurement_CoPilot_Presentation.pdf`

---

## 💡 Pro Tips

1. **Keep it simple**: The HTML presentation is already designed - just customize the text
2. **Use real data**: Replace metrics with actual numbers from your testing
3. **Add your personality**: Include your contact info and team details
4. **Test the PDF**: Open it on different devices to ensure it looks good
5. **File size**: If > 10MB, reduce image quality or remove some graphics

---

## 📋 What Judges Will See

Your presentation covers all judging criteria:

✅ **Technology (40%)**: Slides 4, 5, 9 - Architecture, Stack, Innovation
✅ **Business Value (30%)**: Slides 2, 6, 8, 10 - Problem, Features, ROI, Market
✅ **Presentation (20%)**: All slides - Professional design, clear message
✅ **Originality (10%)**: Slide 9, 11 - Agentic AI differentiation

---

## 🎬 Next Steps

1. **Customize the HTML presentation** (15 minutes)
2. **Take screenshots** from running app (10 minutes)
3. **Export to PDF** (5 minutes)
4. **Review and polish** (10 minutes)
5. **Upload to submission portal** ✅

**Total Time: ~40 minutes**

---

## 📞 Need Help?

- HTML not rendering? Try a different browser (Chrome recommended)
- PDF too large? Remove background images or reduce quality
- Missing screenshots? Use placeholder text and submit anyway

**Good luck with your presentation! 🚀**
