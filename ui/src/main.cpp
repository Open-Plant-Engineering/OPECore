#include <QApplication>
#include <QMessageBox>
#include <Python.h>

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    Py_Initialize();
    PyRun_SimpleString("from yourapp import add_numbers; print(add_numbers(2, 3))");
    Py_Finalize();

    QMessageBox::information(nullptr, "YourApp", "Python executed successfully!");

    return app.exec();
}