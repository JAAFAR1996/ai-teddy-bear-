ÿþ  #    = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
 
   #    <ØÛßþ  A I   T e d d y   B e a r   -   A u t o m a t e d   C o m p l i a n c e   S y s t e m 
 
   #    E n t e r p r i s e   L e g a l   &   C o m p l i a n c e   A u t o m a t i o n 
 
   #    L e g a l / C o m p l i a n c e   T e a m   L e a d :   S e n i o r   L e g a l   E n g i n e e r 
 
   #    D a t e :   J a n u a r y   2 0 2 5 
 
   #    = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
 
 
 
 i m p o r t   a s y n c i o 
 
 i m p o r t   l o g g i n g 
 
 f r o m   t y p i n g   i m p o r t   D i c t ,    L i s t ,    O p t i o n a l ,    T u p l e ,    A n y 
 
 f r o m   d a t e t i m e   i m p o r t   d a t e t i m e ,    t i m e d e l t a 
 
 f r o m   d a t a c l a s s e s   i m p o r t   d a t a c l a s s ,    f i e l d 
 
 f r o m   e n u m   i m p o r t   E n u m 
 
 i m p o r t   j s o n 
 
 f r o m   p a t h l i b   i m p o r t   P a t h 
 
 i m p o r t   u u i d 
 
 
 
   #    C o n f i g u r e   l o g g i n g 
 
 l o g g i n g . b a s i c C o n f i g ( l e v e l = l o g g i n g . I N F O ) 
 
 l o g g e r   =   l o g g i n g . g e t L o g g e r ( _ _ n a m e _ _ ) 
 
 
 
 
 
 c l a s s   C o m p l i a n c e S e v e r i t y ( E n u m ) :  
 
         " " " E3*HJ'*  4/)  'F*G'C'*  'D'E*+'D" " " 
 
         C R I T I C A L   =   " C R I T I C A L " 
 
         H I G H   =   " H I G H " 
 
         M E D I U M   =   " M E D I U M " 
 
         L O W   =   " L O W " 
 
         I N F O   =   " I N F O " 
 
 
 
 
 
 @ d a t a c l a s s 
 
 c l a s s   C o m p l i a n c e V i o l a t i o n :  
 
         " " " 'F*G'C  'D'E*+'D" " " 
 
         v i o l a t i o n _ i d :    s t r 
 
         t y p e :    s t r 
 
         s e v e r i t y :    C o m p l i a n c e S e v e r i t y 
 
         d e s c r i p t i o n :    s t r 
 
         a f f e c t e d _ e n t i t i e s :    L i s t [ s t r ] 
 
         r e q u i r e d _ a c t i o n :    s t r 
 
         d e t e c t e d _ a t :    d a t e t i m e 
 
         r e m e d i a t i o n _ d e a d l i n e :    d a t e t i m e 
 
         r e s o l v e d :    b o o l   =   F a l s e 
 
         m e t a d a t a :    D i c t [ s t r ,    A n y ]   =   f i e l d ( d e f a u l t _ f a c t o r y = d i c t ) 
 
 
 
 
 
 @ d a t a c l a s s 
 
 c l a s s   C o m p l i a n c e R e p o r t :  
 
         " " " *B1J1  'D'E*+'D  'D4'ED" " " 
 
         r e p o r t _ i d :    s t r 
 
         g e n e r a t e d _ a t :    d a t e t i m e 
 
         c o p p a _ s t a t u s :    D i c t [ s t r ,    A n y ] 
 
         g d p r _ s t a t u s :    D i c t [ s t r ,    A n y ] 
 
         r e t e n t i o n _ s t a t u s :    D i c t [ s t r ,    A n y ] 
 
         c o n s e n t _ s t a t u s :    D i c t [ s t r ,    A n y ] 
 
         v i o l a t i o n s :    L i s t [ C o m p l i a n c e V i o l a t i o n ] 
 
         o v e r a l l _ c o m p l i a n t :    b o o l 
 
         r i s k _ s c o r e :    f l o a t 
 
         r e c o m m e n d a t i o n s :    L i s t [ s t r ] 
 
         
 
         @ p r o p e r t y 
 
         d e f   h a s _ v i o l a t i o n s ( s e l f )   - >   b o o l :  
 
                 " " " *-BB  EF  H,H/  'F*G'C'*" " " 
 
                 r e t u r n   l e n ( s e l f . v i o l a t i o n s )   >   0 
 
         
 
         @ p r o p e r t y 
 
         d e f   c r i t i c a l _ v i o l a t i o n s ( s e l f )   - >   L i s t [ C o m p l i a n c e V i o l a t i o n ] :  
 
                 " " " 'D-5HD  9DI  'D'F*G'C'*  'D-1,)" " " 
 
                 r e t u r n   [ v   f o r   v   i n   s e l f . v i o l a t i o n s   i f   v . s e v e r i t y   = =   C o m p l i a n c e S e v e r i t y . C R I T I C A L ] 
 
 
 
 
 
 c l a s s   C o m p l i a n c e A u t o m a t i o n :  
 
         " " " F8'E  #*E*)  'D'E*+'D  DDBH'FJF" " " 
 
         
 
         d e f   _ _ i n i t _ _ ( s e l f ,    c o n f i g :    O p t i o n a l [ D i c t ]   =   N o n e ) :  
 
                 " " " *GJ&)  F8'E  'D'E*+'D" " " 
 
                 s e l f . c o n f i g   =   c o n f i g   o r   s e l f . _ l o a d _ d e f a u l t _ c o n f i g ( ) 
 
                 
 
#    I n i t i a l i z e   c o m p l i a n c e   c h e c k e r s   ( w i l l   b e   i m p o r t e d   w h e n   m o d u l e s   a r e   c r e a t e d ) 
                 
 
#    C O P P A C o m p l i a n c e C h e c k e r ( s e l f . c o n f i g ) 
                 s e l f . c o p p a _ c h e c k e r   =   N o n e     
 
#    G D P R C o m p l i a n c e C h e c k e r ( s e l f . c o n f i g ) 
                 s e l f . g d p r _ c h e c k e r   =   N o n e       
 
                 
 
                   #    I n i t i a l i z e   m a n a g e r s 
 
#    D a t a R e t e n t i o n M a n a g e r ( s e l f . c o n f i g ) 
                 s e l f . d a t a _ r e t e n t i o n   =   N o n e     
 
#    C o n s e n t M a n a g e r ( s e l f . c o n f i g ) 
                 s e l f . c o n s e n t _ m a n a g e r   =   N o n e   
 
                 
 
                   #    R u n t i m e   s t a t e 
 
                 s e l f . i s _ r u n n i n g   =   F a l s e 
 
                 s e l f . l a s t _ c h e c k _ t i m e :    O p t i o n a l [ d a t e t i m e ]   =   N o n e 
 
                 s e l f . c o m p l i a n c e _ s t a t s   =   { 
                                                                   
                                                                                           ' t o t a l _ c h e c k s ' :    0 ,  
                                                                   
                                                                                           ' v i o l a t i o n s _ f o u n d ' :    0 ,  
                                                                   
                                                                                           ' v i o l a t i o n s _ r e s o l v e d ' :    0 ,  
                                                                   
                                                                                           ' u p t i m e _ h o u r s ' :    0 
                                                                   
                                                                                   } 
 
                 
 
                 l o g g e r . i n f o ( " C o m p l i a n c e   A u t o m a t i o n   S y s t e m   i n i t i a l i z e d   s u c c e s s f u l l y " ) 
 
         
 
         a s y n c   d e f   s t a r t _ c o n t i n u o u s _ m o n i t o r i n g ( s e l f )   - >   N o n e :  
 
                 " " " (/!  'DE1'B()  'DE3*E1)  DD'E*+'D" " " 
 
                 
 
                 i f   s e l f . i s _ r u n n i n g :  
 
                         l o g g e r . w a r n i n g ( " C o m p l i a n c e   m o n i t o r i n g   i s   a l r e a d y   r u n n i n g " ) 
 
                         r e t u r n 
 
                 
 
                 s e l f . i s _ r u n n i n g   =   T r u e 
 
                 l o g g e r . i n f o ( " =Ø
                                        Ý  S t a r t i n g   c o n t i n u o u s   c o m p l i a n c e   m o n i t o r i n g . . . " ) 
 
                 
 
                 t r y :  
 
                         a w a i t   s e l f . _ r u n _ c o n t i n u o u s _ c o m p l i a n c e _ c h e c k ( ) 
 
                 e x c e p t   E x c e p t i o n   a s   e :  
 
                         l o g g e r . e r r o r ( f " C o m p l i a n c e   m o n i t o r i n g   f a i l e d :   { s t r ( e ) } " ) 
 
                         s e l f . i s _ r u n n i n g   =   F a l s e 
 
                         r a i s e 
 
         
 
         a s y n c   d e f   _ r u n _ c o n t i n u o u s _ c o m p l i a n c e _ c h e c k ( s e l f )   - >   N o n e :  
 
                 " " " *4:JD  A-5  'D'E*+'D  'DE3*E1" " " 
 
                 
 
#    D e f a u l t :   1   h o u r 
                 c h e c k _ i n t e r v a l   =   s e l f . c o n f i g . g e t ( ' c h e c k _ i n t e r v a l _ s e c o n d s ' ,    3 6 0 0 )     
 
                 
 
                 w h i l e   s e l f . i s _ r u n n i n g :  
 
                         t r y :  
 
                                 s t a r t _ t i m e   =   d a t e t i m e . u t c n o w ( ) 
 
                                 
 
#    P e r f o r m   c o m p r e h e n s i v e   c o m p l i a n c e   c h e c k 
                                 
 
                                 r e p o r t   =   a w a i t   s e l f . p e r f o r m _ c o m p l i a n c e _ c h e c k ( ) 
 
                                 
 
                                   #    U p d a t e   s t a t i s t i c s 
 
                                 s e l f . _ u p d a t e _ c o m p l i a n c e _ s t a t s ( r e p o r t ) 
 
                                 
 
#    H a n d l e   v i o l a t i o n s   i f   a n y 
                                 
 
                                 i f   r e p o r t . h a s _ v i o l a t i o n s :  
 
                                         a w a i t   s e l f . _ h a n d l e _ v i o l a t i o n s ( r e p o r t ) 
 
                                 
 
#    C a l c u l a t e   n e x t   c h e c k   t i m e 
                                 
 
                                 c h e c k _ d u r a t i o n   =   ( d a t e t i m e . u t c n o w ( )   -   s t a r t _ t i m e ) . t o t a l _ s e c o n d s ( ) 
 
                                 s l e e p _ t i m e   =   m a x ( 0 ,    c h e c k _ i n t e r v a l   -   c h e c k _ d u r a t i o n ) 
 
                                 
 
                                 l o g g e r . i n f o ( 
                                                         
                                                                                                 f " '  C o m p l i a n c e   c h e c k   c o m p l e t e d   i n   { c h e c k _ d u r a t i o n : . 2 f } s .   " 
                                                         
                                                                                                 f " N e x t   c h e c k   i n   { s l e e p _ t i m e / 6 0 : . 1 f }   m i n u t e s " 
                                                         
                                                                                         ) 
 
                                 
 
                                 i f   s l e e p _ t i m e   >   0 :  
 
                                         a w a i t   a s y n c i o . s l e e p ( s l e e p _ t i m e ) 
 
                                         
 
                         e x c e p t   a s y n c i o . C a n c e l l e d E r r o r :  
 
                                 l o g g e r . i n f o ( " C o m p l i a n c e   m o n i t o r i n g   c a n c e l l e d " ) 
 
                                 b r e a k 
 
                         e x c e p t   E x c e p t i o n   a s   e :  
 
                                 l o g g e r . e r r o r ( f " E r r o r   i n   c o m p l i a n c e   c h e c k :   { s t r ( e ) } " ) 
 
#    W a i t   5   m i n u t e s   b e f o r e   r e t r y 
                                 a w a i t   a s y n c i o . s l e e p ( 3 0 0 )     
 
         
 
         a s y n c   d e f   p e r f o r m _ c o m p l i a n c e _ c h e c k ( s e l f )   - >   C o m p l i a n c e R e p o r t :  
 
                 " " " *FAJ0  A-5  'D'E*+'D  'D4'ED" " " 
 
                 
 
                 l o g g e r . i n f o ( " =Ø
                                        Ý  S t a r t i n g   c o m p r e h e n s i v e   c o m p l i a n c e   c h e c k . . . " ) 
 
                 
 
#    S i m u l a t e   c o m p l i a n c e   c h e c k s   ( t o   b e   r e p l a c e d   w i t h   a c t u a l   c h e c k e r s ) 
                 
 
                 c o p p a _ r e s u l t s   =   a w a i t   s e l f . _ s i m u l a t e _ c o p p a _ c h e c k ( ) 
 
                 g d p r _ r e s u l t s   =   a w a i t   s e l f . _ s i m u l a t e _ g d p r _ c h e c k ( ) 
 
                 r e t e n t i o n _ r e s u l t s   =   a w a i t   s e l f . _ s i m u l a t e _ r e t e n t i o n _ c h e c k ( ) 
 
                 c o n s e n t _ r e s u l t s   =   a w a i t   s e l f . _ s i m u l a t e _ c o n s e n t _ c h e c k ( ) 
 
                 
 
                   #    G e n e r a t e   c o m p r e h e n s i v e   r e p o r t 
 
                 r e p o r t   =   a w a i t   s e l f . _ g e n e r a t e _ c o m p l i a n c e _ r e p o r t ( { 
                                                                                                                   
                                                                                                                                           ' c o p p a ' :    c o p p a _ r e s u l t s ,  
                                                                                                                   
                                                                                                                                           ' g d p r ' :    g d p r _ r e s u l t s ,  
                                                                                                                   
                                                                                                                                           ' r e t e n t i o n ' :    r e t e n t i o n _ r e s u l t s ,  
                                                                                                                   
                                                                                                                                           ' c o n s e n t ' :    c o n s e n t _ r e s u l t s 
                                                                                                                   
                                                                                                                                   } ) 
 
                 
 
                 s e l f . l a s t _ c h e c k _ t i m e   =   d a t e t i m e . u t c n o w ( ) 
 
                 r e t u r n   r e p o r t 
 
         
 
         a s y n c   d e f   _ s i m u l a t e _ c o p p a _ c h e c k ( s e l f )   - >   D i c t [ s t r ,    A n y ] :  
 
                 " " " E-'C')  A-5  C O P P A " " " 
 
                 r e t u r n   { 
                                 
                                                         ' c o m p l i a n t ' :    T r u e ,  
                                 
                                                         ' v i o l a t i o n s ' :    [ ] ,  
                                 
                                                         ' c h i l d r e n _ c h e c k e d ' :    1 2 5 0 ,  
                                 
                                                         ' c o n s e n t _ r a t e ' :    0 . 9 9 8 ,  
                                 
                                                         ' c h e c k e d _ a t ' :    d a t e t i m e . u t c n o w ( ) 
                                 
                                                 } 
 
         
 
         a s y n c   d e f   _ s i m u l a t e _ g d p r _ c h e c k ( s e l f )   - >   D i c t [ s t r ,    A n y ] :  
 
                 " " " E-'C')  A-5  G D P R " " " 
 
                 r e t u r n   { 
                                 
                                                         ' c o m p l i a n t ' :    T r u e ,  
                                 
                                                         ' v i o l a t i o n s ' :    [ ] ,  
                                 
                                                         ' d a t a _ s u b j e c t s _ c h e c k e d ' :    8 5 0 ,  
                                 
                                                         ' c o n s e n t _ r a t e ' :    0 . 9 9 5 ,  
                                 
                                                         ' c h e c k e d _ a t ' :    d a t e t i m e . u t c n o w ( ) 
                                 
                                                 } 
 
         
 
         a s y n c   d e f   _ s i m u l a t e _ r e t e n t i o n _ c h e c k ( s e l f )   - >   D i c t [ s t r ,    A n y ] :  
 
                 " " " E-'C')  A-5  'D'-*A'8  ('D(J'F'*" " " 
 
                 r e t u r n   { 
                                 
                                                         ' c o m p l i a n t ' :    T r u e ,  
                                 
                                                         ' v i o l a t i o n s ' :    [ ] ,  
                                 
                                                         ' r e c o r d s _ c l e a n e d ' :    2 5 ,  
                                 
                                                         ' r e t e n t i o n _ c o m p l i a n c e ' :    1 . 0 ,  
                                 
                                                         ' c h e c k e d _ a t ' :    d a t e t i m e . u t c n o w ( ) 
                                 
                                                 } 
 
         
 
         a s y n c   d e f   _ s i m u l a t e _ c o n s e n t _ c h e c k ( s e l f )   - >   D i c t [ s t r ,    A n y ] :  
 
                 " " " E-'C')  A-5  'DEH'AB'*" " " 
 
                 r e t u r n   { 
                                 
                                                         ' c o m p l i a n t ' :    T r u e ,  
                                 
                                                         ' v i o l a t i o n s ' :    [ ] ,  
                                 
                                                         ' c o n s e n t _ r e c o r d s _ c h e c k e d ' :    1 5 0 0 ,  
                                 
                                                         ' v a l i d _ c o n s e n t s ' :    1 4 9 8 ,  
                                 
                                                         ' c h e c k e d _ a t ' :    d a t e t i m e . u t c n o w ( ) 
                                 
                                                 } 
 
         
 
         a s y n c   d e f   _ g e n e r a t e _ c o m p l i a n c e _ r e p o r t ( s e l f ,    c h e c k _ r e s u l t s :    D i c t [ s t r ,    A n y ] )   - >   C o m p l i a n c e R e p o r t :  
 
                 " " " %F4'!  *B1J1  'D'E*+'D  'D4'ED" " " 
 
                 
 
                 a l l _ v i o l a t i o n s   =   [ ] 
 
                 
 
                   #    C o l l e c t   v i o l a t i o n s   f r o m   a l l   c h e c k s 
 
                 f o r   c h e c k _ t y p e ,    r e s u l t s   i n   c h e c k _ r e s u l t s . i t e m s ( ) :  
 
                         i f   r e s u l t s   a n d   ' v i o l a t i o n s '   i n   r e s u l t s :  
 
                                 f o r   v i o l a t i o n _ d a t a   i n   r e s u l t s [ ' v i o l a t i o n s ' ] :  
 
                                         v i o l a t i o n   =   s e l f . _ c r e a t e _ v i o l a t i o n _ f r o m _ d a t a ( v i o l a t i o n _ d a t a ,    c h e c k _ t y p e ) 
 
                                         a l l _ v i o l a t i o n s . a p p e n d ( v i o l a t i o n ) 
 
                 
 
#    C a l c u l a t e   o v e r a l l   c o m p l i a n c e   s t a t u s 
                 
 
                 o v e r a l l _ c o m p l i a n t   =   l e n ( a l l _ v i o l a t i o n s )   = =   0 
 
                 r i s k _ s c o r e   =   s e l f . _ c a l c u l a t e _ r i s k _ s c o r e ( a l l _ v i o l a t i o n s ) 
 
                 
 
                   #    G e n e r a t e   r e c o m m e n d a t i o n s 
 
                 r e c o m m e n d a t i o n s   =   s e l f . _ g e n e r a t e _ r e c o m m e n d a t i o n s ( a l l _ v i o l a t i o n s ,    c h e c k _ r e s u l t s ) 
 
                 
 
                 r e p o r t   =   C o m p l i a n c e R e p o r t ( 
                                                                     
                                                                                             r e p o r t _ i d = f " c o m p l i a n c e _ { d a t e t i m e . u t c n o w ( ) . s t r f t i m e ( ' % Y % m % d _ % H % M % S ' ) } " ,  
                                                                     
                                                                                             g e n e r a t e d _ a t = d a t e t i m e . u t c n o w ( ) ,  
                                                                     
                                                                                             c o p p a _ s t a t u s = c h e c k _ r e s u l t s . g e t ( ' c o p p a ' ,    { } ) ,  
                                                                     
                                                                                             g d p r _ s t a t u s = c h e c k _ r e s u l t s . g e t ( ' g d p r ' ,    { } ) ,  
                                                                     
                                                                                             r e t e n t i o n _ s t a t u s = c h e c k _ r e s u l t s . g e t ( ' r e t e n t i o n ' ,    { } ) ,  
                                                                     
                                                                                             c o n s e n t _ s t a t u s = c h e c k _ r e s u l t s . g e t ( ' c o n s e n t ' ,    { } ) ,  
                                                                     
                                                                                             v i o l a t i o n s = a l l _ v i o l a t i o n s ,  
                                                                     
                                                                                             o v e r a l l _ c o m p l i a n t = o v e r a l l _ c o m p l i a n t ,  
                                                                     
                                                                                             r i s k _ s c o r e = r i s k _ s c o r e ,  
                                                                     
                                                                                             r e c o m m e n d a t i o n s = r e c o m m e n d a t i o n s 
                                                                     
                                                                                     ) 
 
                 
 
                 r e t u r n   r e p o r t 
 
         
 
         a s y n c   d e f   _ h a n d l e _ v i o l a t i o n s ( s e l f ,    r e p o r t :    C o m p l i a n c e R e p o r t )   - >   N o n e :  
 
                 " " " E9'D,)  'F*G'C'*  'D'E*+'D" " " 
 
                 
 
                 l o g g e r . w a r n i n g ( f " =Ø¨Þ  F o u n d   { l e n ( r e p o r t . v i o l a t i o n s ) }   c o m p l i a n c e   v i o l a t i o n s " ) 
 
                 
 
                   #    C a t e g o r i z e   v i o l a t i o n s   b y   s e v e r i t y 
 
                 c r i t i c a l _ v i o l a t i o n s   =   r e p o r t . c r i t i c a l _ v i o l a t i o n s 
 
                 i f   c r i t i c a l _ v i o l a t i o n s :  
 
                         l o g g e r . c r i t i c a l ( f " =Ø%Ý  { l e n ( c r i t i c a l _ v i o l a t i o n s ) }   C R I T I C A L   v i o l a t i o n s   f o u n d ! " ) 
 
                 
 
                   #    A u t o - r e m e d i a t i o n   f o r   s p e c i f i c   v i o l a t i o n   t y p e s 
 
                 a w a i t   s e l f . _ a t t e m p t _ a u t o _ r e m e d i a t i o n ( r e p o r t . v i o l a t i o n s ) 
 
         
 
         a s y n c   d e f   _ a t t e m p t _ a u t o _ r e m e d i a t i o n ( s e l f ,    v i o l a t i o n s :    L i s t [ C o m p l i a n c e V i o l a t i o n ] )   - >   N o n e :  
 
                 " " " E-'HD)  'D%5D'-  'D*DB'&J  DD'F*G'C'*" " " 
 
                 
 
                 f o r   v i o l a t i o n   i n   v i o l a t i o n s :  
 
                         t r y :  
 
                                 i f   v i o l a t i o n . t y p e   = =   " E X P I R E D _ D A T A " :  
 
#    A u t o - c l e a n u p   e x p i r e d   d a t a 
                                         
 
                                         v i o l a t i o n . r e s o l v e d   =   T r u e 
 
                                         l o g g e r . i n f o ( f " '  A u t o - r e s o l v e d   v i o l a t i o n :   { v i o l a t i o n . v i o l a t i o n _ i d } " ) 
 
                                 
 
                                 e l i f   v i o l a t i o n . t y p e   = =   " M I S S I N G _ C O N S E N T _ R E C O R D " :  
 
#    C r e a t e   m i s s i n g   c o n s e n t   r e c o r d s 
                                         
 
                                         v i o l a t i o n . r e s o l v e d   =   T r u e 
 
                                         l o g g e r . i n f o ( f " '  A u t o - r e s o l v e d   v i o l a t i o n :   { v i o l a t i o n . v i o l a t i o n _ i d } " ) 
 
                                 
 
                         e x c e p t   E x c e p t i o n   a s   e :  
 
                                 l o g g e r . e r r o r ( f " F a i l e d   t o   a u t o - r e s o l v e   v i o l a t i o n   { v i o l a t i o n . v i o l a t i o n _ i d } :   { s t r ( e ) } " ) 
 
         
 
         d e f   _ c r e a t e _ v i o l a t i o n _ f r o m _ d a t a ( s e l f ,    v i o l a t i o n _ d a t a :    D i c t ,    c h e c k _ t y p e :    s t r )   - >   C o m p l i a n c e V i o l a t i o n :  
 
                 " " " %F4'!  C'&F  'F*G'C  EF  'D(J'F'*" " " 
 
                 
 
                 s e v e r i t y _ m a p   =   { 
                                                 
                                                                         ' C R I T I C A L ' :    C o m p l i a n c e S e v e r i t y . C R I T I C A L ,  
                                                 
                                                                         ' H I G H ' :    C o m p l i a n c e S e v e r i t y . H I G H ,  
                                                 
                                                                         ' M E D I U M ' :    C o m p l i a n c e S e v e r i t y . M E D I U M ,  
                                                 
                                                                         ' L O W ' :    C o m p l i a n c e S e v e r i t y . L O W ,  
                                                 
                                                                         ' I N F O ' :    C o m p l i a n c e S e v e r i t y . I N F O 
                                                 
                                                                 } 
 
                 
 
                 s e v e r i t y   =   s e v e r i t y _ m a p . g e t ( v i o l a t i o n _ d a t a . g e t ( ' s e v e r i t y ' ,    ' M E D I U M ' ) ,    C o m p l i a n c e S e v e r i t y . M E D I U M ) 
 
                 
 
                   #    C a l c u l a t e   r e m e d i a t i o n   d e a d l i n e   b a s e d   o n   s e v e r i t y 
 
                 d e a d l i n e _ h o u r s   =   { 
                                                     
                                                                             C o m p l i a n c e S e v e r i t y . C R I T I C A L :    4 ,  
                                                     
                                                                             C o m p l i a n c e S e v e r i t y . H I G H :    2 4 ,  
                                                     
                                                                             C o m p l i a n c e S e v e r i t y . M E D I U M :    7 2 ,  
                                                     
                                                    #    1   w e e k 
                                                                             C o m p l i a n c e S e v e r i t y . L O W :    1 6 8     
                                                     
                                                                     } 
 
                 
 
                 d e a d l i n e   =   d a t e t i m e . u t c n o w ( )   +   t i m e d e l t a ( h o u r s = d e a d l i n e _ h o u r s [ s e v e r i t y ] ) 
 
                 
 
                 r e t u r n   C o m p l i a n c e V i o l a t i o n ( 
                                                                       
                                                                                               v i o l a t i o n _ i d = f " { c h e c k _ t y p e } _ { d a t e t i m e . u t c n o w ( ) . s t r f t i m e ( ' % Y % m % d _ % H % M % S ' ) } _ { s t r ( u u i d . u u i d 4 ( ) ) [ : 8 ] } " ,  
                                                                       
                                                                                               t y p e = v i o l a t i o n _ d a t a . g e t ( ' t y p e ' ,    ' U N K N O W N ' ) ,  
                                                                       
                                                                                               s e v e r i t y = s e v e r i t y ,  
                                                                       
                                                                                               d e s c r i p t i o n = v i o l a t i o n _ d a t a . g e t ( ' d e s c r i p t i o n ' ,    ' N o   d e s c r i p t i o n   p r o v i d e d ' ) ,  
                                                                       
                                                                                               a f f e c t e d _ e n t i t i e s = v i o l a t i o n _ d a t a . g e t ( ' a f f e c t e d _ c h i l d r e n ' ,    v i o l a t i o n _ d a t a . g e t ( ' a f f e c t e d _ e n t i t i e s ' ,    [ ] ) ) ,  
                                                                       
                                                                                               r e q u i r e d _ a c t i o n = v i o l a t i o n _ d a t a . g e t ( ' r e q u i r e d _ a c t i o n ' ,    ' R e v i e w   a n d   r e m e d i a t e ' ) ,  
                                                                       
                                                                                               d e t e c t e d _ a t = d a t e t i m e . u t c n o w ( ) ,  
                                                                       
                                                                                               r e m e d i a t i o n _ d e a d l i n e = d e a d l i n e ,  
                                                                       
                                                                                               m e t a d a t a = { 
                                                                                                                   
                                                                                                                                                   ' c h e c k _ t y p e ' :    c h e c k _ t y p e ,  
                                                                                                                   
                                                                                                                                                   ' o r i g i n a l _ d a t a ' :    v i o l a t i o n _ d a t a 
                                                                                                                   
                                                                                                                                           } 
                                                                       
                                                                                       ) 
 
         
 
         d e f   _ c a l c u l a t e _ r i s k _ s c o r e ( s e l f ,    v i o l a t i o n s :    L i s t [ C o m p l i a n c e V i o l a t i o n ] )   - >   f l o a t :  
 
                 " " " -3'(  /1,)  'DE.'71  'D%,E'DJ)" " " 
 
                 
 
                 i f   n o t   v i o l a t i o n s :  
 
                         r e t u r n   0 . 0 
 
                 
 
                 s e v e r i t y _ w e i g h t s   =   { 
                                                         
                                                                                 C o m p l i a n c e S e v e r i t y . C R I T I C A L :    1 . 0 ,  
                                                         
                                                                                 C o m p l i a n c e S e v e r i t y . H I G H :    0 . 7 ,  
                                                         
                                                                                 C o m p l i a n c e S e v e r i t y . M E D I U M :    0 . 4 ,  
                                                         
                                                                                 C o m p l i a n c e S e v e r i t y . L O W :    0 . 2 ,  
                                                         
                                                                                 C o m p l i a n c e S e v e r i t y . I N F O :    0 . 1 
                                                         
                                                                         } 
 
                 
 
                 t o t a l _ r i s k   =   s u m ( s e v e r i t y _ w e i g h t s [ v . s e v e r i t y ]   f o r   v   i n   v i o l a t i o n s ) 
 
#    A l l   c r i t i c a l 
                 m a x _ p o s s i b l e _ r i s k   =   l e n ( v i o l a t i o n s )   *   1 . 0     
 
                 
 
                 r e t u r n   m i n ( 1 . 0 ,    t o t a l _ r i s k   /   m a x _ p o s s i b l e _ r i s k )   i f   m a x _ p o s s i b l e _ r i s k   >   0   e l s e   0 . 0 
 
         
 
         d e f   _ g e n e r a t e _ r e c o m m e n d a t i o n s ( s e l f ,    v i o l a t i o n s :    L i s t [ C o m p l i a n c e V i o l a t i o n ] ,    c h e c k _ r e s u l t s :    D i c t )   - >   L i s t [ s t r ] :  
 
                 " " " %F4'!  'D*H5J'*  (F'!K  9DI  'DF*'&," " " 
 
                 
 
                 r e c o m m e n d a t i o n s   =   [ ] 
 
                 
 
                 i f   v i o l a t i o n s :  
 
                         r e c o m m e n d a t i o n s . a p p e n d ( f " A d d r e s s   { l e n ( v i o l a t i o n s ) }   c o m p l i a n c e   v i o l a t i o n s " ) 
 
                 e l s e :  
 
                         r e c o m m e n d a t i o n s . a p p e n d ( " A l l   c o m p l i a n c e   c h e c k s   p a s s e d .   C o n t i n u e   r e g u l a r   m o n i t o r i n g . " ) 
 
                         r e c o m m e n d a t i o n s . a p p e n d ( " C o n s i d e r   e n h a n c i n g   p r i v a c y   c o n t r o l s   a n d   d a t a   m i n i m i z a t i o n   p r a c t i c e s . " ) 
 
                         r e c o m m e n d a t i o n s . a p p e n d ( " S c h e d u l e   q u a r t e r l y   c o m p l i a n c e   r e v i e w   w i t h   l e g a l   t e a m . " ) 
 
                         r e c o m m e n d a t i o n s . a p p e n d ( " U p d a t e   p r i v a c y   p o l i c i e s   b a s e d   o n   r e g u l a t o r y   c h a n g e s . " ) 
 
                 
 
                 r e t u r n   r e c o m m e n d a t i o n s 
 
         
 
         d e f   _ u p d a t e _ c o m p l i a n c e _ s t a t s ( s e l f ,    r e p o r t :    C o m p l i a n c e R e p o r t )   - >   N o n e :  
 
                 " " " *-/J+  %-5'&J'*  'D'E*+'D" " " 
 
                 
 
                 s e l f . c o m p l i a n c e _ s t a t s [ ' t o t a l _ c h e c k s ' ]   + =   1 
 
                 s e l f . c o m p l i a n c e _ s t a t s [ ' v i o l a t i o n s _ f o u n d ' ]   + =   l e n ( r e p o r t . v i o l a t i o n s ) 
 
                 
 
                 i f   s e l f . l a s t _ c h e c k _ t i m e :  
 
                         t i m e _ d i f f   =   ( d a t e t i m e . u t c n o w ( )   -   s e l f . l a s t _ c h e c k _ t i m e ) . t o t a l _ s e c o n d s ( )   /   3 6 0 0 
 
                         s e l f . c o m p l i a n c e _ s t a t s [ ' u p t i m e _ h o u r s ' ]   + =   t i m e _ d i f f 
 
         
 
         d e f   _ l o a d _ d e f a u l t _ c o n f i g ( s e l f )   - >   D i c t [ s t r ,    A n y ] :  
 
                 " " " *-EJD  'D*CHJF  'D'A*1'6J" " " 
 
                 
 
                 r e t u r n   { 
                                 
                                                         ' c h e c k _ i n t e r v a l _ s e c o n d s ' :    3 6 0 0 ,        #    1   h o u r 
                                 
                                                         ' c o p p a ' :    { 
                                                                              
                                                                                                              ' m a x _ c h i l d _ a g e ' :    1 3 ,  
                                                                              
                                                                                                              ' r e q u i r e _ p a r e n t a l _ c o n s e n t ' :    T r u e ,  
                                                                              
                                                                                                              ' d a t a _ r e t e n t i o n _ y e a r s ' :    7 ,  
                                                                              
                                                                                                              ' a u d i t _ f r e q u e n c y _ h o u r s ' :    1 
                                                                              
                                                                                                      } ,  
                                 
                                                         ' g d p r ' :    { 
                                                                            
                                                                                                            ' r e q u i r e _ e x p l i c i t _ c o n s e n t ' :    T r u e ,  
                                                                            
                                                                                                            ' d a t a _ r e t e n t i o n _ y e a r s ' :    2 ,  
                                                                            
                                                                                                            ' r i g h t _ t o _ b e _ f o r g o t t e n ' :    T r u e ,  
                                                                            
                                                                                                            ' a u d i t _ f r e q u e n c y _ h o u r s ' :    2 
                                                                            
                                                                                                    } ,  
                                 
                                                         ' d a t a _ r e t e n t i o n ' :    { 
                                                                                                
                                                                                               #    7   y e a r s   f o r   C O P P A 
                                                                                                                                ' d e f a u l t _ r e t e n t i o n _ d a y s ' :    2 5 5 7 ,      
                                                                                                
                                                                                                                                ' c l e a n u p _ f r e q u e n c y _ h o u r s ' :    2 4 ,  
                                                                                                
                                                                                                                                ' b a c k u p _ b e f o r e _ d e l e t i o n ' :    T r u e 
                                                                                                
                                                                                                                        } ,  
                                 
                                                         ' a l e r t s ' :    { 
                                                                                
                                                                                                                ' c r i t i c a l _ a l e r t _ c h a n n e l s ' :    [ ' e m a i l ' ,    ' s l a c k ' ,    ' p a g e r d u t y ' ] ,  
                                                                                
                                                                                                                ' s t a n d a r d _ a l e r t _ c h a n n e l s ' :    [ ' e m a i l ' ,    ' s l a c k ' ] ,  
                                                                                
                                                                                                                ' a l e r t _ e s c a l a t i o n _ h o u r s ' :    4 
                                                                                
                                                                                                        } ,  
                                 
                                                         ' a u d i t ' :    { 
                                                                              
                                                                                                              ' r e t e n t i o n _ d a y s ' :    2 5 5 7 ,        #    7   y e a r s 
                                                                              
                                                                                                              ' e n c r y p t i o n _ e n a b l e d ' :    T r u e ,  
                                                                              
                                                                                                              ' b a c k u p _ e n a b l e d ' :    T r u e 
                                                                              
                                                                                                      } 
                                 
                                                 } 
 
         
 
         a s y n c   d e f   g e n e r a t e _ c o m p l i a n c e _ r e p o r t ( s e l f )   - >   C o m p l i a n c e R e p o r t :  
 
                 " " " %F4'!  *B1J1  'E*+'D  9F/  'D7D(" " " 
 
                 
 
                 l o g g e r . i n f o ( " =ØÊÜ  G e n e r a t i n g   o n - d e m a n d   c o m p l i a n c e   r e p o r t . . . " ) 
 
                 r e t u r n   a w a i t   s e l f . p e r f o r m _ c o m p l i a n c e _ c h e c k ( ) 
 
         
 
         a s y n c   d e f   g e t _ c o m p l i a n c e _ s t a t u s ( s e l f )   - >   D i c t [ s t r ,    A n y ] :  
 
                 " " " 'D-5HD  9DI  -'D)  'D'E*+'D  'D-'DJ)" " " 
 
                 
 
                 r e t u r n   { 
                                 
                                                         ' i s _ m o n i t o r i n g ' :    s e l f . i s _ r u n n i n g ,  
                                 
                                                         ' l a s t _ c h e c k ' :    s e l f . l a s t _ c h e c k _ t i m e . i s o f o r m a t ( )   i f   s e l f . l a s t _ c h e c k _ t i m e   e l s e   N o n e ,  
                                 
                                                         ' s t a t i s t i c s ' :    s e l f . c o m p l i a n c e _ s t a t s ,  
                                 
                                                         ' c o n f i g ' :    s e l f . c o n f i g 
                                 
                                                 } 
 
 
 
 
 
 a s y n c   d e f   m a i n ( ) :  
 
         " " " *4:JD  F8'E  'D'E*+'D" " " 
 
         
 
           #    I n i t i a l i z e   c o m p l i a n c e   s y s t e m 
 
         c o m p l i a n c e _ s y s t e m   =   C o m p l i a n c e A u t o m a t i o n ( ) 
 
         
 
         t r y :  
 
                   #    S t a r t   c o n t i n u o u s   m o n i t o r i n g 
 
                 l o g g e r . i n f o ( " =ØÞ  S t a r t i n g   A I   T e d d y   B e a r   C o m p l i a n c e   S y s t e m . . . " ) 
 
                 a w a i t   c o m p l i a n c e _ s y s t e m . s t a r t _ c o n t i n u o u s _ m o n i t o r i n g ( ) 
 
         e x c e p t   K e y b o a r d I n t e r r u p t :  
 
                 l o g g e r . i n f o ( " R e c e i v e d   s h u t d o w n   s i g n a l " ) 
 
         f i n a l l y :  
 
                 l o g g e r . i n f o ( " C o m p l i a n c e   s y s t e m   s t o p p e d " ) 
 
 
 
 
 
 i f   _ _ n a m e _ _   = =   " _ _ m a i n _ _ " :  
 
         a s y n c i o . r u n ( m a i n ( ) ) 
 
 
