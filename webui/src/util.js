// Perform a conversion on strings to title case, removing underscores if they exist
function toTitleCase(str) {
  return str
    .replace(/_/g, ' ')
    .split(' ')
    .map((w) => w[0].toUpperCase() + w.substr(1).toLowerCase())
    .join(' ');
}

const Utils = {
  toTitleCase,
};

export default Utils;
