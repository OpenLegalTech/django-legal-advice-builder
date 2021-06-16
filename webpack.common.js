const webpack = require('webpack')
const path = require('path')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const CopyWebpackPlugin = require('copy-webpack-plugin')

module.exports = {
  entry: {
    legal_advice_builder: [
      './legal_advice_builder/assets/scss/style.scss',
      'bootstrap',
      'bootstrap-icons/font/bootstrap-icons.css'
    ]
  },
  resolve: {
    fallback: {
    "fs": false,
    "tls": false,
    "net": false,
    "path": false,
    "zlib": false,
    "http": false,
    "https": false,
    "stream": false,
    "crypto": false,
    "_stream_transform": false,
    "child_process": false,
    "os": false,
    "constants": require.resolve('constants-browserify'),
    "crypto-browserify": require.resolve('crypto-browserify')
    }
  },
  output: {
    libraryTarget: 'this',
    library: '[name]',
    path: path.resolve('./legal_advice_builder/static/'),
    publicPath: '/static/'
  },
  module: {
    rules: [
      {
        test: /\.s?css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader'
        ]
      },
      {
        test: /(fonts|files)\/.*\.(svg|woff2?|ttf|eot|otf)(\?.*)?$/,
        loader: 'file-loader',
        options: {
          name: 'fonts/[name].[ext]'
        }
      },
      {
        test: /\.svg$|\.png$/,
        loader: 'file-loader',
        options: {
          name: 'images/[name].[ext]'
        }
      }
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].css',
      chunkFilename: '[name].css'
    }),
    new webpack.ProvidePlugin({
        process: 'process/browser.js',
        Buffer: ['buffer', 'Buffer'],
      }),
  ]
}