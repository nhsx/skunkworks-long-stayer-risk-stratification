module.exports = {
  devServer: {
    proxy: {
      '^/api': {
        target: 'http://localhost:5000',
        secure: false,
      },
      '^/static': {
        target: 'http://localhost:5000',
        secure: false,
      },
    },
  },
  css: {
    loaderOptions: {
      // pass options to sass-loader
      sass: {
        sassOptions: {
          includePaths: [
            './node_modules/',
            './src/assets/',
          ],
        },
      },
    },
  },
  productionSourceMap: false,
};
