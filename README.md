<p align="center">
  <img src="./img.png" alt="Project Banner" width="100%">
</p>

# ExpenseTracker 🎯

## Basic Details

### Team Name: Thynanana

### Team Members
- Member 1: FATHIMA HUSNA U - TKM COLLEGE OF ENGINEERING
- Member 2: HANA ASHIQUE - TKM COLLEGE OF ENGINEERING

### Hosted Project Link
[mention your project hosted link here]

### Project Description
ExpenseTracker is a smart and student-friendly web application designed to help college students manage their daily expenses effortlessly.  

With a clean interface and reminder functionality, users can record expenses, categorize spending, and stay financially organized. The system uses a lightweight Flask backend and JSON-based storage to ensure simplicity, speed, and reliability.

### The Problem statement
College students often struggle with managing daily expenses due to the absence of structured tracking tools. This results in overspending, poor budgeting habits, and financial stress.

There is a need for a simple, accessible, and effective expense tracking system tailored specifically for students.

--
### The Solution

We developed a Flask-based web application that:

- Allows users to add and manage daily expenses  
- Stores data efficiently using JSON  
- Categorizes expenses for better tracking  
- Includes reminder functionality to promote budgeting discipline  
- Provides a simple and user-friendly interface  

This solution helps students stay financially aware and organized with minimal effort.

---

## Technical Details

### Technologies/Components Used

**For Software:**
- Languages used: Python, HTML, CSS  
- Frameworks used: Flask  
- Libraries used: JSON (built-in Python library)  
- Tools used: VS Code, Git, GitHub
- 
**For Hardware:**
Not applicable (Software-only project)
---

## Features

List the key features of your project:
- Add new expenses with title, category, and amount  
- View recorded expenses in structured format  
- Store expense data in JSON file  
- Reminder functionality for better budgeting  
- Simple and responsive user interface  

---

## Implementation

### For Software:

#### Installation
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
pip install -r requirements.txt
```

#### Run
```bash
python app.py
```
Then open in browser:
```code
http://127.0.0.1:5000
```

### For Hardware:

#### Components Required
[List all components needed with specifications]

#### Circuit Setup
[Explain how to set up the circuit]

---

## Project Documentation

### For Software:

#### Screenshots (Add at least 3)

![Screenshot1](Add screenshot 1 here with proper name)
*Add caption explaining what this shows*

![Screenshot2](Add screenshot 2 here with proper name)
*Add caption explaining what this shows*

![Screenshot3](Add screenshot 3 here with proper name)
*Add caption explaining what this shows*

#### Diagrams

**System Architecture:**

![Architecture Diagram](docs/architecture.png)
*Explain your system architecture - components, data flow, tech stack interaction*

**Application Workflow:**

![Workflow](docs/workflow.png)
*Add caption explaining your workflow*

---

### For Hardware:

#### Schematic & Circuit

![Circuit](Add your circuit diagram here)
*Add caption explaining connections*

![Schematic](Add your schematic diagram here)
*Add caption explaining the schematic*

#### Build Photos

![Team](Add photo of your team here)

![Components](Add photo of your components here)
*List out all components shown*

![Build](Add photos of build process here)
*Explain the build steps*

![Final](Add photo of final product here)
*Explain the final build*

---

## Additional Documentation

### For Web Projects with Backend:

#### API Documentation

**Base URL:** `http://127.0.0.1:5000`

##### Endpoints

**GET /api/endpoint**
- **Description:** loads homepage
- **Parameters:**
  - `param1` (string): [Description]
  - `param2` (integer): [Description]
- **Response:** html page
```json
{
  "status": "success",
  "data": {}
}
```

**POST /api/endpoint** 
- **Description:** adds a new expense
- **Request Body:**
```json
{
  "title": "Food",
  "amount": 150,
  "category": "Daily"
}
```
- **Response:**
```json
{
  "status": "success",
  "message": "Expense added successfully"
}
```

[Add more endpoints as needed...]

---

### For Mobile Apps:

#### App Flow Diagram

![App Flow](docs/app-flow.png)
*Explain the user flow through your application*

#### Installation Guide

**For Android (APK):**
1. Download the APK from [Release Link]
2. Enable "Install from Unknown Sources" in your device settings:
   - Go to Settings > Security
   - Enable "Unknown Sources"
3. Open the downloaded APK file
4. Follow the installation prompts
5. Open the app and enjoy!

**For iOS (IPA) - TestFlight:**
1. Download TestFlight from the App Store
2. Open this TestFlight link: [Your TestFlight Link]
3. Click "Install" or "Accept"
4. Wait for the app to install
5. Open the app from your home screen

**Building from Source:**
```bash
# For Android
flutter build apk
# or
./gradlew assembleDebug

# For iOS
flutter build ios
# or
xcodebuild -workspace App.xcworkspace -scheme App -configuration Debug
```

---

### For Hardware Projects:

#### Bill of Materials (BOM)

| Component | Quantity | Specifications | Price | Link/Source |
|-----------|----------|----------------|-------|-------------|
| Arduino Uno | 1 | ATmega328P, 16MHz | ₹450 | [Link] |
| LED | 5 | Red, 5mm, 20mA | ₹5 each | [Link] |
| Resistor | 5 | 220Ω, 1/4W | ₹1 each | [Link] |
| Breadboard | 1 | 830 points | ₹100 | [Link] |
| Jumper Wires | 20 | Male-to-Male | ₹50 | [Link] |
| [Add more...] | | | | |

**Total Estimated Cost:** ₹[Amount]

#### Assembly Instructions

**Step 1: Prepare Components**
1. Gather all components listed in the BOM
2. Check component specifications
3. Prepare your workspace
![Step 1](images/assembly-step1.jpg)
*Caption: All components laid out*

**Step 2: Build the Power Supply**
1. Connect the power rails on the breadboard
2. Connect Arduino 5V to breadboard positive rail
3. Connect Arduino GND to breadboard negative rail
![Step 2](images/assembly-step2.jpg)
*Caption: Power connections completed*

**Step 3: Add Components**
1. Place LEDs on breadboard
2. Connect resistors in series with LEDs
3. Connect LED cathodes to GND
4. Connect LED anodes to Arduino digital pins (2-6)
![Step 3](images/assembly-step3.jpg)
*Caption: LED circuit assembled*

**Step 4: [Continue for all steps...]**

**Final Assembly:**
![Final Build](images/final-build.jpg)
*Caption: Completed project ready for testing*

---

### For Scripts/CLI Tools:

#### Command Reference

**Basic Usage:**
```bash
python script.py [options] [arguments]
```

**Available Commands:**
- `command1 [args]` - Description of what command1 does
- `command2 [args]` - Description of what command2 does
- `command3 [args]` - Description of what command3 does

**Options:**
- `-h, --help` - Show help message and exit
- `-v, --verbose` - Enable verbose output
- `-o, --output FILE` - Specify output file path
- `-c, --config FILE` - Specify configuration file
- `--version` - Show version information

**Examples:**

```bash
# Example 1: Basic usage
python script.py input.txt

# Example 2: With verbose output
python script.py -v input.txt

# Example 3: Specify output file
python script.py -o output.txt input.txt

# Example 4: Using configuration
python script.py -c config.json --verbose input.txt
```

#### Demo Output

**Example 1: Basic Processing**

**Input:**
```
This is a sample input file
with multiple lines of text
for demonstration purposes
```

**Command:**
```bash
python script.py sample.txt
```

**Output:**
```
Processing: sample.txt
Lines processed: 3
Characters counted: 86
Status: Success
Output saved to: output.txt
```

**Example 2: Advanced Usage**

**Input:**
```json
{
  "name": "test",
  "value": 123
}
```

**Command:**
```bash
python script.py -v --format json data.json
```

**Output:**
```
[VERBOSE] Loading configuration...
[VERBOSE] Parsing JSON input...
[VERBOSE] Processing data...
{
  "status": "success",
  "processed": true,
  "result": {
    "name": "test",
    "value": 123,
    "timestamp": "2024-02-07T10:30:00"
  }
}
[VERBOSE] Operation completed in 0.23s
```

---

## Project Demo

### Video
[Add your demo video link here - YouTube, Google Drive, etc.]

*Explain what the video demonstrates - key features, user flow, technical highlights*

### Additional Demos
[Add any extra demo materials/links - Live site, APK download, online demo, etc.]

---

## AI Tools Used (Optional - For Transparency Bonus)

If you used AI tools during development, document them here for transparency:

**Tool Used:** [GitHub Copilot, ChatGPT,Claude]

**Purpose:** 
AI tools were used as development assistants throughout the project lifecycle for:

- Generating frontend UI components
- Structuring Flask backend routes
- Debugging errors and resolving integration issues
- Designing reminder and parsing logic
- Improving code organization and documentation
- 
**Key Prompts Used:**
- "Create a REST API endpoint for user authentication"
- "Debug this async function that's causing race conditions"
- "Optimize this database query for better performance"

**Percentage of AI-generated code:** 
Approximately 70–80% of boilerplate and UI logic was AI-assisted.
**Human Contributions:**
- System design and feature architecture
- Backend integration and data flow logic
- Expense tracking functionality
- JSON data handling
- Testing, debugging, deployment, and optimization
- Final refinement and project documentation

*Note: Proper documentation of AI usage demonstrates transparency and earns bonus points in evaluation!*

---
## Team Contributions

- **FATHIMA HUSNA U**
  - Project planning and feature design  
  - Backend structure setup using Flask  
  - Integration of expense logic and JSON storage  
  - Testing, debugging, and deployment  
  - Repository management using Git  

- **HANA ASHIQUE**
  - Frontend layout design and UI refinement  
  - Feature enhancement and reminder logic integration  
  - User experience improvements  
  - Testing and validation of application flow  
  - Documentation and submission preparation  
---

## License

This project is licensed under the [LICENSE_NAME] License - see the [LICENSE](LICENSE) file for details.

**Common License Options:**
- MIT License (Permissive, widely used)
- Apache 2.0 (Permissive with patent grant)
- GPL v3 (Copyleft, requires derivative works to be open source)

---

Made with ❤️ at TinkerHub
