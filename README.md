**University Notes Project**

The University Notes Project is a web application designed to streamline the management, sharing, and accessibility of academic notes within a university or educational institution.
It offers a centralized platform where students and faculty can upload, organize, and access course-related materials, fostering collaborative learning and resource sharing.

  **Installation**

To use the University Notes Project locally, follow these steps:

* Clone the repository:

```bash
git clone https://github.com/wathika-eng/uninotes_refactor --depth 1 && cd uninotes_refactor
```

* Create a virtual environment (optional but recommended):

```bash
python -m venv .venv
```

* Activate the virtual environment:
  * On Windows:

  ```bash
  .venv\Scripts\activate
  ```

  * On macOS/Linux:

  ```bash
  source .venv/bin/activate
  ```

* Install the required dependencies:

##### prefer to use uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`

```bash
pip install -r requirements.txt
```

* Set up the database:

```bash
python manage.py migrate
```

* Create a superuser (optional):

```bash
python manage.py createsuperuser
```

* Run the development server:

```bash
python manage.py runserver
```

Open the website locaaly: <http://localhost:8000>

#### known bugs: <https://stackoverflow.com/questions/5420789/how-to-install-psycopg2-with-pip-on-python/13158616>
<!-- **Usage**

Upon installation, users can sign up, log in, and start uploading and managing their notes. They can search for specific courses or subjects, upload materials, create study groups, and collaborate with peers for better academic performance.

**Configuration**

The project uses Django as the primary framework and requires specific configurations for database connections, environment variables for security, and storage options. Refer to the documentation or .env file for configuration details.

**Contributing**

Contributions to the University Notes Project are welcome! Fork the repository, make changes, and submit a pull request following the contribution guidelines specified in the CONTRIBUTING.md file.

**License**

This project is licensed under the MIT License. See the LICENSE file for more details. -->

<!-- **Key Features**

* Note Upload: Users can upload notes, presentations, and study materials in various formats (PDFs, documents, images) for specific courses or subjects.
* Course Management: Organize notes by courses, departments, semesters, or academic years for easy navigation and retrieval.
* User Authentication: Secure user authentication and authorization to manage access control and ensure data privacy.
* Search and Filtering: Robust search functionalities to easily find notes by keywords, course names, or categories.
* Collaborative Sharing: Share notes within study groups, classes, or publicly, promoting collaboration and knowledge exchange.
* Responsive Design: A user-friendly interface accessible across devices, enabling students to access materials anytime, anywhere. -->