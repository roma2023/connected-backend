const axios = require('axios');
const cheerio = require('cheerio');

async function getDownloadLink(bookLink) {
  try {
    //console.log(`Starting download link extraction for book link: ${bookLink}`);
    
    const url = bookLink;
    //console.log(`Fetching URL: ${url}`);
    
    const response = await axios.get(url);
    //console.log(`Received response with status: ${response.status}`);
    
    const $ = cheerio.load(response.data);
    let libgenLiLink = null;

    // Find the libgen.li link
    $('td a').each((i, elem) => {
      const href = $(elem).attr('href');
      //console.log(`Inspecting link ${i}: ${href}`);
      
      if (href && href.includes('libgen.li')) {
        libgenLiLink = href;
        //console.log(`Found libgen.li link: ${libgenLiLink}`);
        return false; // break the loop
      }
    });

    if (!libgenLiLink) {
      console.log('libgen.li link not found');
      console.log(JSON.stringify({ error: 'libgen.li link not found' }));
      return;
    }

    // Fetch the libgen.li link
    const libgenLiResponse = await axios.get(libgenLiLink);
    //console.log(`Received response from libgen.li with status: ${libgenLiResponse.status}`);
    
    const libgenLiPage = cheerio.load(libgenLiResponse.data);
    let downloadLink = null;

    // Find the "GET" link
    libgenLiPage('td a').each((i, elem) => {
      const h2 = libgenLiPage(elem).find('h2');
      //console.log(`Inspecting link ${i}: ${libgenLiPage(elem).attr('href')}`);
      
      if (h2.length && h2.text().trim() === 'GET') {
        downloadLink = libgenLiPage(elem).attr('href');
        //console.log(`Found download link: ${downloadLink}`);
        return false; // break the loop
      }
    });

    if (downloadLink) {
      // console.log(`Download link found: ${downloadLink}`);
      console.log(JSON.stringify({ downloadLink }));
      return downloadLink;
    } else {
      console.log('Download link not found');
      console.log(JSON.stringify({ error: 'Download link not found' }));
    }
  } catch (error) {
    console.error('Error fetching download page:', error);
  }
}

const bookLink = process.argv[2];
if (bookLink) {
  getDownloadLink(bookLink);
} else {
  console.error('No book link provided');
}