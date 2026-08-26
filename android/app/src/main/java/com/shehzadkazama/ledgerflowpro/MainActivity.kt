package com.shehzadkazama.ledgerflowpro

import android.app.Activity
import android.os.Bundle
import android.util.Log
import android.view.KeyEvent
import android.view.View
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.ProgressBar
import android.widget.TextView

/**
 * LedgerFlowPro mobile shell.
 *
 * Loads the live Streamlit site (already connected to Supabase) inside a
 * full-screen WebView. If anything fails to set up, the actual error is
 * shown on screen instead of the app silently closing, so it can be
 * screenshotted and diagnosed.
 */
class MainActivity : Activity() {

    private var webView: WebView? = null
    private val appUrl = "https://ledgerflowpro-app.streamlit.app/"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            setContentView(R.layout.activity_main)

            val webView = findViewById<WebView>(R.id.webview)
            val progress = findViewById<ProgressBar>(R.id.progress)
            this.webView = webView

            val settings: WebSettings = webView.settings
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.databaseEnabled = true
            settings.cacheMode = WebSettings.LOAD_DEFAULT
            settings.loadWithOverviewMode = true
            settings.useWideViewPort = true
            settings.mediaPlaybackRequiresUserGesture = false

            webView.webViewClient = object : WebViewClient() {
                override fun onPageFinished(view: WebView?, url: String?) {
                    super.onPageFinished(view, url)
                    progress.visibility = View.GONE
                }
            }

            webView.webChromeClient = object : WebChromeClient() {
                override fun onProgressChanged(view: WebView?, newProgress: Int) {
                    progress.progress = newProgress
                    progress.visibility = if (newProgress >= 100) View.GONE else View.VISIBLE
                }
            }

            webView.loadUrl(appUrl)
        } catch (t: Throwable) {
            Log.e("LedgerFlowPro", "Crash while starting app", t)
            showError(t)
        }
    }

    private fun showError(t: Throwable) {
        val tv = TextView(this)
        tv.text = "LedgerFlowPro could not start:\n\n" + Log.getStackTraceString(t)
        tv.setPadding(32, 80, 32, 32)
