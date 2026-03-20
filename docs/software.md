---
title: QRB Labs software
---

/* Styles for the gallery container */
<style>
.gallery-no-lightbox {
  display: grid;
  /*
    Creates a responsive grid. It will try to make columns at least 250px wide.
    If there's space, it will create more columns.
    "1fr" means each column will take up an equal fraction of the remaining space.
  */
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px; /* Space between items */
  margin: 20px 0;
  padding: 0;
  list-style: none;
}

/* Styles for each individual gallery item */
.gallery-item {
  border: 1px solid #ddd;
  border-radius: 5px;
  overflow: hidden; /* Ensures images don't spill out */
  text-align: center;
  background-color: #f9f9f9;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: transform 0.2s ease-in-out;
  display: flex; /* Use flexbox to control layout inside the item */
  flex-direction: column; /* Stack image and text vertically */
}

.gallery-item:hover {
  transform: translateY(-5px); /* Slight lift on hover */
}

/* Styles for the images within gallery items */
.gallery-item img {
  display: block; /* Removes bottom space */
  width: 100%;
  height: 180px; /* Fixed height for uniformity, adjust as needed */
  object-fit: cover; /* Scales image while maintaining aspect ratio, cropping if necessary */
  object-position: center; /* Centers the image */
  /* No border-bottom needed here as the <p> tag has padding */
}

/* Styles for the captions */
.gallery-item p {
  padding: 10px 15px;
  margin: 0; /* Remove default margin */
  font-size: 0.95em;
  color: #333;
  flex-grow: 1; /* Allows the text to take up available space */
  display: flex; /* Center the text vertically if needed */
  align-items: center; /* Centers text vertically */
  justify-content: center; /* Centers text horizontally */
}

.gallery-item p strong {
  color: #000; /* Make the bold part stand out more */
}
</style>

### MDB

MDB is QRB Labs minimalist open source mining monitoring and management software, built on top of ggthe ELK stack.

<img alt="QRB Labs MDB architecture" src="images/mdb.svg" />

Features:

- ultra lightweight machine database in Google sheets
- tools to monitor and control miners via miner API
- environment monitoring via temperature and himidity sensors
- network video recording and analysis for security cameras
- automated feedback control of water circulation in water curtains
- dashboard and search engine for history and real-time analysis
- rack visualization integrated with real-time status monitoring

<div class="gallery-no-lightbox">

  <div class="gallery-item">
    <img src="/images/mdbvideosearch.png" alt="MDB Video Search Interface Screenshot">
    <p><strong>Video Search & Analysis:</strong> Quickly find and review footage from your security cameras.</p>
  </div>

  <div class="gallery-item">
    <img src="/images/monelk.png" alt="MDB ELK Stack Dashboard Screenshot">
    <p><strong>ELK Stack Dashboard:</strong> Monitor your mining operations with comprehensive real-time data visualization.</p>
  </div>

  <div class="gallery-item">
    <img src="/images/mdbrackview.png" alt="MDB Rack View Screenshot">
    <p><strong>Rack Visualization:</strong> See the real-time status and health of your mining racks at a glance.</p>
  </div>

</div>
