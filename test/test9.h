#ifndef TEST9_H
#define TEST9_H

/** This is a function. */
int foo(int x)
{
    return x + 5;
}

/**
 * This is a class.
 *
 * I think it's a cool class.
 */
class Test
{
protected:
    /**
     * This is an internal empty class.
     *
     * It's empty and very useless.
     */
    class Meta
    {
    };
    
    /**
     * This is a class method.
     *
     * I think it's a cool class method.
     */
    void simpleMethod();

public:    
    /**
     * This is another class method.
     *
     * This is not so cool.
     */
    void anotherSimpleMethod(int x, bool y = false);
    
    /**
     * This is a class member variable.
     *
     * I think it's a cool class member variable.
     */
    int m_x;
};

/**
@entity class_Test__func_simpleMethod

This is a replaced doc.

It's still a simple class method, but with a new doc!
*/

#endif
