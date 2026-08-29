package com.example.calculator

import android.os.Bundle
import android.view.View
import androidx.activity.ComponentActivity
import com.example.calculator.R.layout.activity_main
import android.widget.EditText
import android.widget.TextView

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(activity_main)

    }

    private var valOne: String? = ""
    private var valTwo: String? = ""
    private var opType: String? = null
    private var currExp = ""

    fun setValue(view: View?) {
        if (view != null) {
            val currVal = view.tag.toString()
            if (currVal == "+" || currVal == "-" || currVal == "*" || currVal == "/" || currVal == "=") {
                if (opType == null) {
                    opType = currVal
                    display(currVal)
                }
            } else {
                if (opType == null) {
                    valOne += currVal
                    display(currVal)
                } else {
                    valTwo += currVal
                    display(currVal)
                }
            }
        }
    }

    fun compute(view: View?) {
        if (opType == null || valOne == "" || valTwo == "") return
        var ans: Float = 0.0F
        var valOneCal: Float = valOne?.toFloat() ?: 0.0F
        var valTwoCal: Float = valTwo?.toFloat() ?: 0.0F
        when (opType) {
            "+" -> ans = valOneCal + valTwoCal
            "-" -> ans = valOneCal - valTwoCal
            "*" -> ans = valOneCal * valTwoCal
            "/" -> ans = valOneCal / valTwoCal
            else -> println("There seems to be a problem.")
        }
        currExp = ""
        display(ans.toString())
    }

    fun clear(view: View?) {
        currExp = ""
        valOne = ""
        valTwo = ""
        opType = null
        display(currExp)
    }

    private fun display(string: String) {
        //var editText = findViewById<EditText>(R.id.editText)
        currExp += string
        val editText = findViewById<View>(R.id.resultText) as EditText
        editText.setText(currExp, TextView.BufferType.EDITABLE)
    }
}

