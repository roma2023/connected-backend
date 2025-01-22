# **ConnectED Backend**

## **Overview**  
The ConnectED Backend is the core service responsible for content management, processing, and distribution in the ConnectED system. It interacts with multiple educational content providers (e.g., Khan Academy, Google Books, Open edX, Coursera, Udemy) to retrieve and process content, which is then converted into audio using AI-driven text-to-speech technologies. The backend supports queuing and scheduling for multiple radio channels to broadcast educational content to students in underserved areas.  

While the architecture is well-defined, **this codebase is currently under development and is not functional yet**. Contributions and feedback are welcome as we continue to build and refine the system.

---

## **Architecture**  

Below is a high-level diagram of the backend architecture:  

![ConnectED Architecture](<add-your-image-file-path-or-hosted-url>)  

### **Key Components**  
1. **Frontend Service**: Provides teachers and NGOs with tools to upload content, monitor broadcasts, and schedule lessons.  
2. **API Service**: Interfaces with external educational content providers (e.g., Khan Academy, Open edX) to retrieve relevant content.  
3. **AI Agent (Notebook LLM)**: Converts retrieved educational content into audio files using text-to-speech processing.  
4. **Distributed Queues**: Manages broadcast schedules and organizes audio files by radio channel.  
5. **Broadcaster Services**: Responsible for sending processed audio to specific FM radio frequencies.  
6. **Cloud Hosting**: The entire backend system is deployed in the cloud for scalability and reliability, supporting platforms like AWS, Azure, or GCP.

---

## **Current Status**  
This repository is still a work in progress. While we have finalized the architecture and initial design, the following features are currently being implemented:  
- Integration with external content providers (e.g., Google Books, Open edX).  
- AI-powered audio content conversion using Notebook LLM or Google Cloud Text-to-Speech.  
- Queue and broadcasting services for multiple radio channels.  
- API endpoints for the frontend to manage content uploads and schedules.

Please note that **the codebase is not yet functional**. We will provide updates as we progress in building the backend.

---

## **Installation and Setup (Planned)**  
Once the backend is operational, the following steps will guide you to set up the system locally:  

### **Prerequisites**  
- **Python 3.9+**  
- **Docker** (for containerized services)  
- **PostgreSQL** (or another compatible relational database)  
- **RabbitMQ** or **Kafka** (for distributed queuing)  

### **Steps to Set Up (Coming Soon)**  
1. Clone the repository:  
   ```bash
   git clone <repository-url>
   cd connected-backend
   ```
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt  
   ```

3. Run the development server:
   ```bash
   python manage.py runserver  
   ```
   
4. Set up environment variables:  
   ```env
   DATABASE_URL=postgresql://<user>:<password>@localhost/<database_name>  
   SECRET_KEY=<your-secret-key>  
   CLOUD_API_KEY=<cloud-api-key>
   ```

Detailed setup instructions will be added as development progresses.

---

## **Future Roadmap**  
- **Phase 1**: API Integration with educational content providers (e.g., Khan Academy, Google Books).  
- **Phase 2**: Implement AI-powered text-to-speech services and content queuing.  
- **Phase 3**: Develop and test broadcaster services for multi-channel support.  
- **Phase 4**: Deploy the backend to cloud platforms (e.g., AWS, Azure, or GCP).  

---

## **Contribution Guidelines**  
We welcome contributions to this project! However, since the codebase is under active development, we recommend the following steps for contributors:  

1. **Fork the Repository**:  
   Click the **Fork** button on the repository page to create a copy of the repository under your GitHub account.  

2. **Clone Your Fork**:  
   ```bash
   git clone <your-fork-url>  
   cd connected-backend  
   ```
3. **Create a Feature Branch**:
   ```bash
   git checkout -b feature-name
   ```
   
5. **Make Changes and Commit**:  
   ```bash
   git add .  
   git commit -m "Description of changes"
   ```

6. **Push to Your Fork**:  
   ```bash
   git push origin feature-name
   ```

7. **Submit a Pull Request**:  
   Open a pull request to the main branch of the original repository and include a clear description of your changes.

For detailed contribution guidelines, see the `CONTRIBUTING.md` file (to be added).  

---

## **Acknowledgements**  
This project is part of the ConnectED initiative and is being developed by **MART Innovation - ED7**. Special thanks to OpenAI’s ChatGPT for providing assistance with documentation, brainstorming, and technical recommendations.  

---

## **License**  
This repository is licensed under the MIT License. See the `LICENSE` file for details.  
