ÿþ  #  ! / u s r / b i n / e n v   p y t h o n 3 
 
 " " " 
 
 C o m p r e h e n s i v e   U n i t   T e s t s   f o r   C h i l d   R e p o s i t o r y 
 
 T e s t s   a l l   C R U D   o p e r a t i o n s ,    s e a r c h   f u n c t i o n a l i t y ,    a n d   b u s i n e s s   l o g i c 
 
 " " " 
 
 
 
 i m p o r t   p y t e s t 
 
 i m p o r t   a s y n c i o 
 
 i m p o r t   s q l i t e 3 
 
 i m p o r t   t e m p f i l e 
 
 i m p o r t   o s 
 
 f r o m   d a t e t i m e   i m p o r t   d a t e t i m e ,    d a t e ,    t i m e d e l t a 
 
 f r o m   t y p i n g   i m p o r t   L i s t ,    D i c t ,    A n y 
 
 f r o m   u n i t t e s t . m o c k   i m p o r t   M o c k ,    p a t c h ,    M a g i c M o c k 
 
 
 
   #    I m p o r t   o u r   m o d u l e s 
 
 f r o m   s r c . i n f r a s t r u c t u r e . p e r s i s t e n c e . c h i l d _ s q l i t e _ r e p o s i t o r y   i m p o r t   C h i l d S Q L i t e R e p o s i t o r y 
 
 f r o m   s r c . d o m a i n . e n t i t i e s . c h i l d   i m p o r t   C h i l d 
 
 f r o m   s r c . d o m a i n . r e p o s i t o r i e s . b a s e   i m p o r t   S e a r c h C r i t e r i a ,    Q u e r y O p t i o n s ,    S o r t O r d e r ,    B u l k O p e r a t i o n R e s u l t 
 
 
 
 
 
 @ p y t e s t . f i x t u r e 
 
 d e f   t e m p _ d b ( ) :  
 
         " " " C r e a t e   a   t e m p o r a r y   d a t a b a s e   f o r   t e s t i n g " " " 
 
         f d ,    p a t h   =   t e m p f i l e . m k s t e m p ( s u f f i x = ' . d b ' ) 
 
         o s . c l o s e ( f d ) 
 
         y i e l d   p a t h 
 
         o s . u n l i n k ( p a t h ) 
 
 
 
 
 
 @ p y t e s t . f i x t u r e 
 
 d e f   m o c k _ s e s s i o n _ f a c t o r y ( ) :  
 
         " " " M o c k   s e s s i o n   f a c t o r y   f o r   t e s t i n g " " " 
 
         r e t u r n   M o c k ( ) 
 
 
 
 
 
 @ p y t e s t . f i x t u r e 
 
 d e f   c h i l d _ r e p o s i t o r y ( t e m p _ d b ,    m o c k _ s e s s i o n _ f a c t o r y ) :  
 
         " " " C r e a t e   a   C h i l d   r e p o s i t o r y   i n s t a n c e   f o r   t e s t i n g " " " 
 
         r e p o   =   C h i l d S Q L i t e R e p o s i t o r y ( m o c k _ s e s s i o n _ f a c t o r y ,    t e m p _ d b ) 
 
         r e t u r n   r e p o 
 
 
 
 
 
 @ p y t e s t . f i x t u r e 
 
 d e f   s a m p l e _ c h i l d _ d a t a ( ) :  
 
         " " " S a m p l e   c h i l d   d a t a   f o r   t e s t i n g " " " 
 
         r e t u r n   { 
                         
                                         ' i d ' :    ' t e s t - c h i l d - 0 0 1 ' ,  
                         
                                         ' n a m e ' :    ' A l i c e ' ,  
                         
                                         ' a g e ' :    8 ,  
                         
                                         ' d a t e _ o f _ b i r t h ' :    d a t e ( 2 0 1 5 ,    5 ,    1 5 ) ,  
                         
                                         ' g e n d e r ' :    ' f e m a l e ' ,  
                         
                                         ' p e r s o n a l i t y _ t r a i t s ' :    [ ' c u r i o u s ' ,    ' c r e a t i v e ' ,    ' e n e r g e t i c ' ] ,  
                         
                                         ' l e a r n i n g _ p r e f e r e n c e s ' :    { ' v i s u a l ' :    0 . 8 ,    ' a u d i t o r y ' :    0 . 6 ,    ' k i n e s t h e t i c ' :    0 . 4 } ,  
                         
                                         ' c o m m u n i c a t i o n _ s t y l e ' :    ' p l a y f u l ' ,  
                         
                                         ' m a x _ d a i l y _ i n t e r a c t i o n _ t i m e ' :    3 6 0 0 ,  
                         
                                         ' t o t a l _ i n t e r a c t i o n _ t i m e ' :    1 2 0 0 ,  
                         
                                         ' l a s t _ i n t e r a c t i o n ' :    d a t e t i m e . n o w ( )   -   t i m e d e l t a ( h o u r s = 2 ) ,  
                         
                                         ' a l l o w e d _ t o p i c s ' :    [ ' s c i e n c e ' ,    ' s t o r i e s ' ,    ' g a m e s ' ] ,  
                         
                                         ' r e s t r i c t e d _ t o p i c s ' :    [ ' v i o l e n c e ' ,    ' a d u l t _ c o n t e n t ' ] ,  
                         
                                         ' l a n g u a g e _ p r e f e r e n c e ' :    ' e n ' ,  
                         
                                         ' c u l t u r a l _ b a c k g r o u n d ' :    ' a m e r i c a n ' ,  
                         
                                         ' p a r e n t a l _ c o n t r o l s ' :    { ' b e d t i m e _ m o d e ' :    T r u e ,    ' c o n t e n t _ f i l t e r ' :    ' s t r i c t ' } ,  
                         
                                         ' e m e r g e n c y _ c o n t a c t s ' :    [ 
                                                                                        
                                                                                                                { ' n a m e ' :    ' M o m ' ,    ' p h o n e ' :    ' + 1 2 3 4 5 6 7 8 9 0 ' ,    ' r e l a t i o n ' :    ' p a r e n t ' } ,  
                                                                                        
                                                                                                                { ' n a m e ' :    ' D a d ' ,    ' p h o n e ' :    ' + 1 2 3 4 5 6 7 8 9 1 ' ,    ' r e l a t i o n ' :    ' p a r e n t ' } 
                                                                                        
                                                                                                        ] ,  
                         
                                         ' m e d i c a l _ n o t e s ' :    ' N o   k n o w n   a l l e r g i e s ' ,  
                         
                                         ' e d u c a t i o n a l _ l e v e l ' :    ' e l e m e n t a r y ' ,  
                         
                                         ' s p e c i a l _ n e e d s ' :    [ ' a d h d _ s u p p o r t ' ] ,  
                         
                                         ' i s _ a c t i v e ' :    T r u e ,  
                         
                                         ' p r i v a c y _ s e t t i n g s ' :    { ' d a t a _ s h a r i n g ' :    F a l s e ,    ' a n a l y t i c s ' :    T r u e } ,  
                         
                                         ' c u s t o m _ s e t t i n g s ' :    { ' f a v o r i t e _ c o l o r ' :    ' b l u e ' ,    ' p e t _ n a m e ' :    ' F l u f f y ' } 
                         
                                 } 
 
 
 
 
 
 @ p y t e s t . f i x t u r e 
 
 d e f   s a m p l e _ c h i l d ( s a m p l e _ c h i l d _ d a t a ) :  
 
         " " " C r e a t e   a   s a m p l e   C h i l d   e n t i t y " " " 
 
         r e t u r n   C h i l d ( * * s a m p l e _ c h i l d _ d a t a ) 
 
 
 
 
 
 c l a s s   T e s t C h i l d R e p o s i t o r y B a s i c O p e r a t i o n s :  
 
         " " " T e s t   b a s i c   C R U D   o p e r a t i o n s " " " 
 
         
 
         @ p y t e s t . m a r k . a s y n c i o 
 
         a s y n c   d e f   t e s t _ c r e a t e _ c h i l d ( s e l f ,    c h i l d _ r e p o s i t o r y ,    s a m p l e _ c h i l d ) :  
 
                 " " " T e s t   c r e a t i n g   a   n e w   c h i l d " " " 
 
                   #    A c t 
 
                 r e s u l t   =   a w a i t   c h i l d _ r e p o s i t o r y . c r e a t e ( s a m p l e _ c h i l d ) 
 
                 
 
                   #    A s s e r t 
 
                 a s s e r t   r e s u l t   i s   n o t   N o n e 
 
                 a s s e r t   r e s u l t . i d   i s   n o t   N o n e 
 
                 a s s e r t   r e s u l t . n a m e   = =   s a m p l e _ c h i l d . n a m e 
 
                 a s s e r t   r e s u l t . a g e   = =   s a m p l e _ c h i l d . a g e 
 
                 a s s e r t   r e s u l t . c r e a t e d _ a t   i s   n o t   N o n e 
 
         
 
         @ p y t e s t . m a r k . a s y n c i o 
 
         a s y n c   d e f   t e s t _ g e t _ c h i l d _ b y _ i d ( s e l f ,    c h i l d _ r e p o s i t o r y ,    s a m p l e _ c h i l d ) :  
 
                 " " " T e s t   r e t r i e v i n g   a   c h i l d   b y   I D " " " 
 
                   #    A r r a n g e 
 
                 c r e a t e d _ c h i l d   =   a w a i t   c h i l d _ r e p o s i t o r y . c r e a t e ( s a m p l e _ c h i l d ) 
 
                 
 
                   #    A c t 
 
                 r e t r i e v e d _ c h i l d   =   a w a i t   c h i l d _ r e p o s i t o r y . g e t _ b y _ i d ( c r e a t e d _ c h i l d . i d ) 
 
                 
 
                   #    A s s e r t 
 
                 a s s e r t   r e t r i e v e d _ c h i l d   i s   n o t   N o n e 
 
                 a s s e r t   r e t r i e v e d _ c h i l d . i d   = =   c r e a t e d _ c h i l d . i d 
 
                 a s s e r t   r e t r i e v e d _ c h i l d . n a m e   = =   s a m p l e _ c h i l d . n a m e 
 
                 a s s e r t   r e t r i e v e d _ c h i l d . p e r s o n a l i t y _ t r a i t s   = =   s a m p l e _ c h i l d . p e r s o n a l i t y _ t r a i t s 
 
         
 
         @ p y t e s t . m a r k . a s y n c i o 
 
         a s y n c   d e f   t e s t _ u p d a t e _ c h i l d ( s e l f ,    c h i l d _ r e p o s i t o r y ,    s a m p l e _ c h i l d ) :  
 
                 " " " T e s t   u p d a t i n g   a n   e x i s t i n g   c h i l d " " " 
 
                   #    A r r a n g e 
 
                 c r e a t e d _ c h i l d   =   a w a i t   c h i l d _ r e p o s i t o r y . c r e a t e ( s a m p l e _ c h i l d ) 
 
                 c r e a t e d _ c h i l d . n a m e   =   ' A l i c e   U p d a t e d ' 
 
                 c r e a t e d _ c h i l d . a g e   =   9 
 
                 
 
                   #    A c t 
 
                 u p d a t e d _ c h i l d   =   a w a i t   c h i l d _ r e p o s i t o r y . u p d a t e ( c r e a t e d _ c h i l d ) 
 
                 
 
                   #    A s s e r t 
 
                 a s s e r t   u p d a t e d _ c h i l d . n a m e   = =   ' A l i c e   U p d a t e d ' 
 
                 a s s e r t   u p d a t e d _ c h i l d . a g e   = =   9 
 
         
 
         @ p y t e s t . m a r k . a s y n c i o 
 
         a s y n c   d e f   t e s t _ d e l e t e _ c h i l d ( s e l f ,    c h i l d _ r e p o s i t o r y ,    s a m p l e _ c h i l d ) :  
 
                 " " " T e s t   s o f t   d e l e t i n g   a   c h i l d " " " 
 
                   #    A r r a n g e 
 
                 c r e a t e d _ c h i l d   =   a w a i t   c h i l d _ r e p o s i t o r y . c r e a t e ( s a m p l e _ c h i l d ) 
 
                 
 
                   #    A c t 
 
                 d e l e t e _ r e s u l t   =   a w a i t   c h i l d _ r e p o s i t o r y . d e l e t e ( c r e a t e d _ c h i l d . i d ) 
 
                 
 
                   #    A s s e r t 
 
                 a s s e r t   d e l e t e _ r e s u l t   i s   T r u e 
 
         
 
         @ p y t e s t . m a r k . a s y n c i o 
 
         a s y n c   d e f   t e s t _ l i s t _ c h i l d r e n ( s e l f ,    c h i l d _ r e p o s i t o r y ) :  
 
                 " " " T e s t   l i s t i n g   m u l t i p l e   c h i l d r e n " " " 
 
                   #    A r r a n g e 
 
                 c h i l d r e n _ d a t a   =   [ 
                                                   
                                                                           { ' n a m e ' :    ' A l i c e ' ,    ' a g e ' :    8 } ,  
                                                   
                                                                           { ' n a m e ' :    ' B o b ' ,    ' a g e ' :    1 0 } ,  
                                                   
                                                                           { ' n a m e ' :    ' C h a r l i e ' ,    ' a g e ' :    6 } 
                                                   
                                                                   ] 
 
                 
 
                 c r e a t e d _ c h i l d r e n   =   [ ] 
 
                 f o r   d a t a   i n   c h i l d r e n _ d a t a :  
 
                         c h i l d   =   C h i l d ( 
                                                     
                                                                                     n a m e = d a t a [ ' n a m e ' ] ,  
                                                     
                                                                                     a g e = d a t a [ ' a g e ' ] ,  
                                                     
                                                                                     p e r s o n a l i t y _ t r a i t s = [ ] ,  
                                                     
                                                                                     l e a r n i n g _ p r e f e r e n c e s = { } 
                                                     
                                                                             ) 
 
                         c r e a t e d _ c h i l d r e n . a p p e n d ( a w a i t   c h i l d _ r e p o s i t o r y . c r e a t e ( c h i l d ) ) 
 
                 
 
                   #    A c t 
 
                 a l l _ c h i l d r e n   =   a w a i t   c h i l d _ r e p o s i t o r y . l i s t ( ) 
 
                 
 
                   #    A s s e r t 
 
                 a s s e r t   l e n ( a l l _ c h i l d r e n )   > =   3 
 
 
 
 
 
 c l a s s   T e s t C h i l d R e p o s i t o r y S e a r c h A n d F i l t e r i n g :  
 
         " " " T e s t   s e a r c h   a n d   f i l t e r i n g   f u n c t i o n a l i t y " " " 
 
         
 
         @ p y t e s t . m a r k . a s y n c i o 
 
         a s y n c   d e f   t e s t _ f i n d _ b y _ n a m e ( s e l f ,    c h i l d _ r e p o s i t o r y ,    s a m p l e _ c h i l d ) :  
 
                 " " " T e s t   f i n d i n g   a   c h i l d   b y   n a m e " " " 
 
                   #    A r r a n g e 
 
                 a w a i t   c h i l d _ r e p o s i t o r y . c r e a t e ( s a m p l e _ c h i l d ) 
 
                 
 
                   #    A c t 
 
                 f o u n d _ c h i l d   =   a w a i t   c h i l d _ r e p o s i t o r y . f i n d _ b y _ n a m e ( s a m p l e _ c h i l d . n a m e ) 
 
                 
 
                   #    A s s e r t 
 
                 a s s e r t   f o u n d _ c h i l d   i s   n o t   N o n e 
 
                 a s s e r t   f o u n d _ c h i l d . n a m e   = =   s a m p l e _ c h i l d . n a m e 
 
         
 
         @ p y t e s t . m a r k . a s y n c i o 
 
         a s y n c   d e f   t e s t _ f i n d _ b y _ a g e _ r a n g e ( s e l f ,    c h i l d _ r e p o s i t o r y ) :  
 
                 " " " T e s t   f i n d i n g   c h i l d r e n   b y   a g e   r a n g e " " " 
 
                   #    A r r a n g e 
 
                 c h i l d r e n   =   [ 
                                         
                                                                 C h i l d ( n a m e = ' Y o u n g ' ,    a g e = 5 ,    p e r s o n a l i t y _ t r a i t s = [ ] ,    l e a r n i n g _ p r e f e r e n c e s = { } ) ,  
                                         
                                                                 C h i l d ( n a m e = ' M i d d l e ' ,    a g e = 8 ,    p e r s o n a l i t y _ t r a i t s = [ ] ,    l e a r n i n g _ p r e f e r e n c e s = { } ) ,  
                                         
                                                                 C h i l d ( n a m e = ' O l d e r ' ,    a g e = 1 2 ,    p e r s o n a l i t y _ t r a i t s = [ ] ,    l e a r n i n g _ p r e f e r e n c e s = { } ) 
                                         
                                                         ] 
 
                 
 
                 f o r   c h i l d   i n   c h i l d r e n :  
 
                         a w a i t   c h i l d _ r e p o s i t o r y . c r e a t e ( c h i l d ) 
 
                 
 
                   #    A c t 
 
                 c h i l d r e n _ i n _ r a n g e   =   a w a i t   c h i l d _ r e p o s i t o r y . f i n d _ b y _ a g e _ r a n g e ( 6 ,    1 0 ) 
 
                 
 
                   #    A s s e r t 
 
                 a s s e r t   l e n ( c h i l d r e n _ i n _ r a n g e )   > =   1 
 
                 a g e s   =   [ c h i l d . a g e   f o r   c h i l d   i n   c h i l d r e n _ i n _ r a n g e ] 
 
                 a s s e r t   a l l ( 6   < =   a g e   < =   1 0   f o r   a g e   i n   a g e s ) 
 
 
 
 
 
 c l a s s   T e s t C h i l d R e p o s i t o r y B u s i n e s s L o g i c :  
 
         " " " T e s t   b u s i n e s s   l o g i c   a n d   a d v a n c e d   f u n c t i o n a l i t y " " " 
 
         
 
         @ p y t e s t . m a r k . a s y n c i o 
 
         a s y n c   d e f   t e s t _ g e t _ c h i l d r e n _ n e e d i n g _ a t t e n t i o n ( s e l f ,    c h i l d _ r e p o s i t o r y ) :  
 
                 " " " T e s t   f i n d i n g   c h i l d r e n   t h a t   n e e d   a t t e n t i o n " " " 
 
                   #    A r r a n g e 
 
                 o l d _ i n t e r a c t i o n _ c h i l d   =   C h i l d ( 
                                                                             
                                                                                                     n a m e = ' O l d   I n t e r a c t i o n ' ,    a g e = 8 ,  
                                                                             
                                                                                                     l a s t _ i n t e r a c t i o n = d a t e t i m e . n o w ( )   -   t i m e d e l t a ( d a y s = 5 ) ,  
                                                                             
                                                                                                     p e r s o n a l i t y _ t r a i t s = [ ] ,    l e a r n i n g _ p r e f e r e n c e s = { } 
                                                                             
                                                                                             ) 
 
                 s p e c i a l _ n e e d s _ c h i l d   =   C h i l d ( 
                                                                         
                                                                                                 n a m e = ' S p e c i a l   N e e d s ' ,    a g e = 8 ,  
                                                                         
                                                                                                 s p e c i a l _ n e e d s = [ ' a u t i s m ' ] ,  
                                                                         
                                                                                                 p e r s o n a l i t y _ t r a i t s = [ ] ,    l e a r n i n g _ p r e f e r e n c e s = { } 
                                                                         
                                                                                         ) 
 
                 
 
                 a w a i t   c h i l d _ r e p o s i t o r y . c r e a t e ( o l d _ i n t e r a c t i o n _ c h i l d ) 
 
                 a w a i t   c h i l d _ r e p o s i t o r y . c r e a t e ( s p e c i a l _ n e e d s _ c h i l d ) 
 
                 
 
                   #    A c t 
 
                 a t t e n t i o n _ n e e d e d   =   a w a i t   c h i l d _ r e p o s i t o r y . g e t _ c h i l d r e n _ n e e d i n g _ a t t e n t i o n ( ) 
 
                 
 
                   #    A s s e r t 
 
                 a s s e r t   l e n ( a t t e n t i o n _ n e e d e d )   > =   2 
 
         
 
         @ p y t e s t . m a r k . a s y n c i o 
 
         a s y n c   d e f   t e s t _ g e t _ e n g a g e m e n t _ i n s i g h t s ( s e l f ,    c h i l d _ r e p o s i t o r y ,    s a m p l e _ c h i l d ) :  
 
                 " " " T e s t   g e n e r a t i n g   e n g a g e m e n t   i n s i g h t s " " " 
 
                   #    A r r a n g e 
 
                 c r e a t e d _ c h i l d   =   a w a i t   c h i l d _ r e p o s i t o r y . c r e a t e ( s a m p l e _ c h i l d ) 
 
                 
 
                   #    A c t 
 
                 i n s i g h t s   =   a w a i t   c h i l d _ r e p o s i t o r y . g e t _ e n g a g e m e n t _ i n s i g h t s ( c r e a t e d _ c h i l d . i d ) 
 
                 
 
                   #    A s s e r t 
 
                 a s s e r t   i n s i g h t s   i s   n o t   N o n e 
 
                 a s s e r t   ' c h i l d _ i d '   i n   i n s i g h t s 
 
                 a s s e r t   ' e n g a g e m e n t _ l e v e l '   i n   i n s i g h t s 
 
                 a s s e r t   ' r e c o m m e n d a t i o n s '   i n   i n s i g h t s 
 
                 a s s e r t   i n s i g h t s [ ' c h i l d _ i d ' ]   = =   c r e a t e d _ c h i l d . i d 
 
 
 
 
 
 i f   _ _ n a m e _ _   = =   ' _ _ m a i n _ _ ' :  
 
           #    R u n   t e s t s 
 
         p y t e s t . m a i n ( [ _ _ f i l e _ _ ,    ' - v ' ,    ' - - t b = s h o r t ' ] ) 
 
 
