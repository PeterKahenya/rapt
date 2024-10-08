package rapt.chat.raptandroid.data.source

import android.content.Context
import android.provider.ContactsContract
import android.util.Log

data class PhoneContact(
    val id: String,
    val name: String,
    val phone: String
)

class RaptContentProvider constructor(
    private val context: Context,
) {
    fun getContacts(): List<PhoneContact> {
        try {
            val contactsList = mutableListOf<PhoneContact>()
            val projection = arrayOf(
                ContactsContract.CommonDataKinds.Phone.CONTACT_ID,
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
                ContactsContract.CommonDataKinds.Phone.NUMBER
            )
            context.contentResolver.query(
                ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                projection,
                null,
                null,
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME + " ASC"
            )?.use { cursor ->
                val idIndex =
                    cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.CONTACT_ID)
                val nameIndex =
                    cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
                val numberIndex =
                    cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
                if (idIndex != -1 && nameIndex != -1 && numberIndex != -1) {
                    while (cursor.moveToNext()) {
                        val id = cursor.getString(idIndex)
                        val name = cursor.getString(nameIndex)
                        val number = cursor.getString(numberIndex)
                        contactsList.add(
                            PhoneContact(
                                id,
                                phone = number.filterNot { it.isWhitespace() },
                                name = name
                            )
                        )
                    }
                }
            }
            return contactsList
        } catch (e: SecurityException) {
            Log.e("RaptContentProvider", "SecurityException: ${e.message}")
            return emptyList()
        }
    }
}
