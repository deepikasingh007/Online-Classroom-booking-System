# Online Classroom Booking System

## Description
The **Online Classroom Booking System** is a web-based application designed for booking classrooms, managing room availability, and ensuring necessary resources like projectors are available. It allows users to view the classroom capacity and availability of projectors while booking the classroom.

### Key Features:
- **User Registration/Login**: Users can create an account and log in.
- **Classroom Booking**: Users can book available classrooms based on date, time, and capacity requirements.
- **View Classrooms Availability**: Displays a list of classrooms with available times and their capacity.
- **Projector Availability**: Shows if the projector is available for the selected classroom.
- **Search by Room Capacity and Projector Availability**: Filters available classrooms based on the required capacity and whether a projector is available.

## Technologies Used
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQL (MySQL/PostgreSQL)
- **Version Control**: Git, GitLab

## Installation Instructions
To run this project locally, follow these steps:
1. Clone the repository:
   ```bash
    `git clone <https://gitlab.com/devikajaincambridge/se-project-sem-3>
    ```
2. Install dependencies
Navigate to the project directory and install the required Python packages:

  ```bash
    cd <project_directory>
    pip install -r requirements.txt   
  ```
3. Set up the database
You need to set up your database using MySQL or PostgreSQL. The database will contain tables for classrooms, bookings, and users.
Create a database with the appropriate schema for the application.
Make sure to update the database connection configuration in your config.py

4. Run the Flask application
Once the database is set up, run the Flask development server:

```bash
    flask run
```
This will start the server at http://127.0.0.1:5000 on your local machine.

## Breakdown of Sections:
1. **Description**: Provides an overview of the system and its key features.
2. **Technologies Used**: Lists the technologies used in your project.
3. **Installation Instructions**: A step-by-step guide to setting up the project on a local machine.
4. **Usage**: Explains how users can sign up, log in, and use the system.
5. **Project Structure**: Describes the file organization in your project.
6. **Database Schema**: Details the database structure.
7. **License**: Mentions the project's licensing (MIT License).
8. **Contributing**: Explains how others can contribute to your project.
9. **Contact**: Gives contact information for further inquiries.

## License
This project is licensed under the MIT License - see **the LICENSE file for details.**

## Contributing
Contributions are welcome! If you find a bug or would like to add a feature, feel free to fork the repository, create a new branch, and submit a pull request.
**Fork the repository.**
**Create a new branch (git checkout -b feature-name).**
**Make your changes.**
**Commit your changes (git commit -am 'Add new feature').**
**Push to the branch (git push origin feature-name).**
**Submit a pull request.**
## Contact
For any inquiries, please contact us at [devikajaincambridge@gmail.com] [deeps25104@gmail.com] or through our issue tracker on GitLab.
