const path = require("path");

module.exports = {
   outputDir: path.resolve(__dirname, "../server/public"),
   configureWebpack: {
      devServer: {
         host: "localhost",
      },
   },
};