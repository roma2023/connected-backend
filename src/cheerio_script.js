const axios = require('axios');
const cheerio = require('cheerio');

async function searchLibraryGenesis(bookName) {
  try {
    const response = await axios.get('https://libgen.is/search.php', {
      params: {
        req: bookName,
        lg_topic: 'libgen',
        open: 0,
        view: 'simple',
        res: 25,
        phrase: 1,
        column: 'def'
      }
    });

    const $ = cheerio.load(response.data);
    const booksList = $('tr[valign="top"]');
    const bookMetadata = [];

    booksList.each((i, tr) => {
      const title = $(tr).find('td').eq(2).find('a').text().trim().toLowerCase();
      const author = $(tr).find('td').eq(1).find('a').text().trim().toLowerCase();
      const bookLink = $(tr).find('td').eq(2).find('a').attr('href');
      const year = $(tr).find('td').eq(4).text().trim();
      const publisher = $(tr).find('td').eq(3).text().trim();
      const format = $(tr).find('td').eq(8).text().trim();
      const size = $(tr).find('td').eq(7).text().trim();

      const metadata = {
        title,
        author,
        year,
        publisher,
        format,
        size,
        link: bookLink
      };

      bookMetadata.push(metadata);
    });

    console.log(JSON.stringify(bookMetadata));
  } catch (error) {
    console.error('Error fetching data from Library Genesis:', error);
  }
}

const bookName = process.argv[2];
searchLibraryGenesis(bookName);