function syncReadFile(filename) {
  const {readFileSync, promises: fsPromises} = require('fs');
  
  const contents = readFileSync(filename, 'utf-8');

  const arr = contents.split(/\r?\n/);

  return arr;
}

var enableDays = syncReadFile('./calendar.txt');
enableDays.length = enableDays.length - 1;

console.log(enableDays);