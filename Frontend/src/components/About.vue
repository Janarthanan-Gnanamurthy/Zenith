<!-- src/components/AboutPage.vue -->
<template>
<div class="flex min-h-screen">
    <!-- Right side - About Content -->
    <div class="w-full flex items-center justify-center p-8">
    <div class="w-full overflow-y-auto max-h-screen">
        <div class="text-center mb-8 lg:hidden">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-16 h-16 mx-auto text-primary">
            <path d="M18.375 2.25c-1.035 0-1.875.84-1.875 1.875v15.75c0 1.035.84 1.875 1.875 1.875h.75c1.035 0 1.875-.84 1.875-1.875V4.125c0-1.036-.84-1.875-1.875-1.875h-.75zM9.75 8.625c0-1.036.84-1.875 1.875-1.875h.75c1.036 0 1.875.84 1.875 1.875v11.25c0 1.035-.84 1.875-1.875 1.875h-.75a1.875 1.875 0 01-1.875-1.875V8.625zM3 13.125c0-1.036.84-1.875 1.875-1.875h.75c1.036 0 1.875.84 1.875 1.875v6.75c0 1.035-.84 1.875-1.875 1.875h-.75A1.875 1.875 0 013 19.875v-6.75z" />
        </svg>
        <h1 class="text-2xl font-bold mt-2">Zenith</h1>
        </div>
        
        <div class="flex flex-col md:flex-row items-center gap-6 mb-8">
        <div class="w-32 h-32 bg-gradient-to-tr from-purple-600 to-indigo-500 rounded-full flex items-center justify-center">
            <span class="text-3xl font-bold text-white">JG</span>
        </div>
        <div>
            <h1 class="text-3xl font-extrabold mb-2">Janarthanan Gnanamurthy</h1>
            <p class="text-base-content/70 mb-3">AI Developer & Data Science Specialist</p>
            <div class="flex flex-wrap gap-3">
            <a href="mailto:janagnanam12@gmail.com" class="btn btn-sm btn-outline gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                Email
            </a>
            <a href="https://linkedin.com/in/janarthanangm" target="_blank" class="btn btn-sm btn-outline gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                </svg>
                LinkedIn
            </a>
            <a href="https://github.com/Janarthanan-Gnanamurthy" target="_blank" class="btn btn-sm btn-outline gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                GitHub
            </a>
            <a href="tel:+919003119904" class="btn btn-sm btn-outline gap-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                Phone
            </a>
            </div>
        </div>
        </div>
        
        <!-- About Me -->
        <div class="mb-8">
        <h2 class="text-2xl font-bold mb-4 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            About Me
        </h2>
        <div class="bg-base-200 rounded-lg p-6 shadow-md">
            <p class="mb-3">
            I am a passionate AI Developer and Data Science specialist with expertise in developing intelligent systems and data-driven solutions. My focus lies in AI, Machine Learning, and Natural Language Processing, with practical experience in building applications that leverage cutting-edge technologies.
            </p>
            <p>
            Currently pursuing degrees in Data Science & Programming from IIT Madras and Artificial Intelligence & Data Science from Anna University, I combine strong theoretical knowledge with practical implementation skills to create impactful solutions.
            </p>
        </div>
        </div>
        
        <!-- Skills -->
        <div class="mb-8">
        <h2 class="text-2xl font-bold mb-4 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Skills
        </h2>
        <div class="bg-base-200 rounded-lg p-6 shadow-md">
            <div class="mb-4">
            <h3 class="font-semibold mb-2">Programming & Web Technologies</h3>
            <div class="flex flex-wrap gap-2">
                <span class="badge badge-primary">Java</span>
                <span class="badge badge-primary">Python</span>
                <span class="badge badge-primary">SQL</span>
                <span class="badge badge-primary">JavaScript</span>
                <span class="badge badge-primary">Git</span>
                <span class="badge badge-primary">Bash Scripts</span>
                <span class="badge badge-primary">FastAPI</span>
                <span class="badge badge-primary">React.js</span>
                <span class="badge badge-primary">Next.js</span>
                <span class="badge badge-primary">Vue.js</span>
                <span class="badge badge-primary">Nuxt.js</span>
                <span class="badge badge-primary">Firebase</span>
            </div>
            </div>
            <div>
            <h3 class="font-semibold mb-2">AI & Data Science</h3>
            <div class="flex flex-wrap gap-2">
                <span class="badge badge-primary">AI</span>
                <span class="badge badge-primary">NLP</span>
                <span class="badge badge-primary">PyTorch</span>
                <span class="badge badge-primary">TensorFlow</span>
                <span class="badge badge-primary">LLMs</span>
                <span class="badge badge-primary">LangChain</span>
                <span class="badge badge-primary">Unsloth AI</span>
                <span class="badge badge-primary">Transformers</span>
                <span class="badge badge-primary">AWS</span>
                <span class="badge badge-primary">Software Testing</span>
            </div>
            </div>
        </div>
        </div>
        
        <!-- Achievements -->
        <div class="mb-8">
        <h2 class="text-2xl font-bold mb-4 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
            Achievements
        </h2>
        <div class="space-y-4">
            <div class="bg-base-200 rounded-lg p-6 shadow-md">
            <div class="flex justify-between items-start">
                <h3 class="font-semibold">Smart Industry 4.0 Hackathon Winner</h3>
                <span class="badge badge-accent">₹1,25,000</span>
            </div>
            <p class="text-sm text-base-content/70">Chennai Institute of Technology</p>
            <p class="mt-2">Developed a collaborative robot with humanoid features using state-of-the-art RL algorithms and 3D Gaussian splatting, increasing task efficiency by 50% and delivering 2-3X performance gains.</p>
            </div>
            
            <div class="bg-base-200 rounded-lg p-6 shadow-md">
            <div class="flex justify-between items-start">
                <h3 class="font-semibold">Sensathon 2024 Hackathon Runner-up</h3>
                <span class="badge badge-accent">₹15,000</span>
            </div>
            <p class="text-sm text-base-content/70">Sona college of technology Pvt Ltd</p>
            <p class="mt-2">Built a wearable device for Parkinson's disease patients that predicts tremors with high accuracy using embedded sensors and ML models, with automatic emergency notifications.</p>
            </div>
        </div>
        </div>
        
        <!-- Education -->
        <div class="mb-8">
        <h2 class="text-2xl font-bold mb-4 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path d="M12 14l9-5-9-5-9 5 9 5z" />
            <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" />
            </svg>
            Education
        </h2>
        <div class="space-y-4">
            <div class="bg-base-200 rounded-lg p-6 shadow-md">
            <div class="flex justify-between items-start">
                <div>
                <h3 class="font-semibold">Indian Institute of Technology Madras</h3>
                <p class="text-sm">B.Sc, Data Science & Programming</p>
                </div>
                <div class="text-right">
                <span class="badge badge-primary">CGPA: 8.38</span>
                <p class="text-sm text-base-content/70">2022 - Present</p>
                </div>
            </div>
            <p class="mt-2 text-sm">Relevant Coursework: Machine Learning, Artificial Intelligence, Deep Learning, Business Analytics, Software Testing, Database Management Systems, Statistics</p>
            </div>
            
            <div class="bg-base-200 rounded-lg p-6 shadow-md">
            <div class="flex justify-between items-start">
                <div>
                <h3 class="font-semibold">Anna University Regional Campus, Coimbatore</h3>
                <p class="text-sm">B.Tech, Artificial Intelligence and Data Science</p>
                </div>
                <div class="text-right">
                <span class="badge badge-primary">CGPA: 8.10</span>
                <p class="text-sm text-base-content/70">2022 - Present</p>
                </div>
            </div>
            <p class="mt-2 text-sm">Relevant Coursework: Data Structures and Algorithms, Artificial Intelligence, Machine Learning, Deep Learning, Soft Computing, Object-Oriented Programming, Data Analytics and Visualization</p>
            </div>
        </div>
        </div>
        
        <!-- Navigation Button -->
        <div class="text-center mb-4">
        <router-link to="/" class="text-primary hover:underline flex items-center justify-center gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Dashboard
        </router-link>
        </div>
    </div>
    </div>
</div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
</script>