ÿþ" " " 
 
 V e c t o r   M e m o r y   S t o r e   -   I n f r a s t r u c t u r e   f o r   s e m a n t i c   m e m o r y   s e a r c h 
 
 " " " 
 
 
 
 i m p o r t   n u m p y   a s   n p 
 
 f r o m   t y p i n g   i m p o r t   D i c t ,    L i s t ,    O p t i o n a l 
 
 f r o m   c o l l e c t i o n s   i m p o r t   d e f a u l t d i c t 
 
 
 
 t r y :  
 
         i m p o r t   f a i s s 
 
         F A I S S _ A V A I L A B L E   =   T r u e 
 
 e x c e p t   I m p o r t E r r o r :  
 
         F A I S S _ A V A I L A B L E   =   F a l s e 
 
 
 
 t r y :  
 
         f r o m   s k l e a r n . c l u s t e r   i m p o r t   D B S C A N 
 
         S K L E A R N _ A V A I L A B L E   =   T r u e 
 
 e x c e p t   I m p o r t E r r o r :  
 
         S K L E A R N _ A V A I L A B L E   =   F a l s e 
 
 
 
 f r o m   . . . d o m a i n . m e m o r y . m o d e l s   i m p o r t   M e m o r y ,    M e m o r y I m p o r t a n c e 
 
 
 
 
 
 c l a s s   V e c t o r M e m o r y S t o r e :  
 
         " " " V e c t o r - b a s e d   m e m o r y   s t o r a g e   f o r   s e m a n t i c   s e a r c h " " " 
 
 
 
         d e f   _ _ i n i t _ _ ( s e l f ,    d i m e n s i o n :    i n t   =   3 8 4 ) :  
 
                 s e l f . d i m e n s i o n   =   d i m e n s i o n 
 
                 s e l f . m e m o r i e s :    D i c t [ i n t ,    M e m o r y ]   =   { } 
 
                 s e l f . c u r r e n t _ i d x   =   0 
 
                 
 
                 i f   F A I S S _ A V A I L A B L E :  
 
                         s e l f . i n d e x   =   f a i s s . I n d e x F l a t L 2 ( d i m e n s i o n ) 
 
                 e l s e :  
 
                         s e l f . i n d e x   =   N o n e 
 
 
 
         d e f   a d d _ m e m o r y ( s e l f ,    m e m o r y :    M e m o r y )   - >   N o n e :  
 
                 " " " A d d   m e m o r y   w i t h   e m b e d d i n g   t o   v e c t o r   s t o r e " " " 
 
                 i f   m e m o r y . e m b e d d i n g   i s   n o t   N o n e   a n d   s e l f . i n d e x   i s   n o t   N o n e :  
 
                         s e l f . i n d e x . a d d ( m e m o r y . e m b e d d i n g . r e s h a p e ( 1 ,    - 1 ) ) 
 
                         s e l f . m e m o r i e s [ s e l f . c u r r e n t _ i d x ]   =   m e m o r y 
 
                         s e l f . c u r r e n t _ i d x   + =   1 
 
 
 
         d e f   s e a r c h _ s i m i l a r ( s e l f ,    q u e r y _ e m b e d d i n g :    n p . n d a r r a y ,    k :    i n t   =   5 )   - >   L i s t [ M e m o r y ] :  
 
                 " " " S e a r c h   f o r   s i m i l a r   m e m o r i e s " " " 
 
                 i f   n o t   s e l f . i n d e x   o r   s e l f . i n d e x . n t o t a l   = =   0 :  
 
                         r e t u r n   [ ] 
 
 
 
                 d i s t a n c e s ,    i n d i c e s   =   s e l f . i n d e x . s e a r c h ( 
                                                                                                
                                                                                                                        q u e r y _ e m b e d d i n g . r e s h a p e ( 1 ,    - 1 ) ,    m i n ( k ,    s e l f . i n d e x . n t o t a l ) ) 
 
 
 
                 s i m i l a r _ m e m o r i e s   =   [ ] 
 
                 f o r   i d x ,    d i s t a n c e   i n   z i p ( i n d i c e s [ 0 ] ,    d i s t a n c e s [ 0 ] ) :  
 
                         i f   i d x   ! =   - 1 :        #    V a l i d   i n d e x 
 
                                 m e m o r y   =   s e l f . m e m o r i e s [ i d x ] 
 
                                 s i m i l a r _ m e m o r i e s . a p p e n d ( m e m o r y ) 
 
 
 
                 r e t u r n   s i m i l a r _ m e m o r i e s 
 
 
 
         d e f   c l u s t e r _ m e m o r i e s ( s e l f ,    m i n _ s a m p l e s :    i n t   =   3 )   - >   D i c t [ i n t ,    L i s t [ M e m o r y ] ] :  
 
                 " " " C l u s t e r   m e m o r i e s   b y   s i m i l a r i t y " " " 
 
                 i f   n o t   S K L E A R N _ A V A I L A B L E   o r   n o t   s e l f . i n d e x   o r   s e l f . i n d e x . n t o t a l   <   m i n _ s a m p l e s :  
 
                         r e t u r n   { } 
 
 
 
                   #    G e t   a l l   e m b e d d i n g s 
 
                 e m b e d d i n g s   =   [ ] 
 
                 m e m o r y _ l i s t   =   [ ] 
 
 
 
                 f o r   i d x ,    m e m o r y   i n   s e l f . m e m o r i e s . i t e m s ( ) :  
 
                         i f   m e m o r y . e m b e d d i n g   i s   n o t   N o n e :  
 
                                 e m b e d d i n g s . a p p e n d ( m e m o r y . e m b e d d i n g ) 
 
                                 m e m o r y _ l i s t . a p p e n d ( m e m o r y ) 
 
 
 
                 i f   n o t   e m b e d d i n g s :  
 
                         r e t u r n   { } 
 
 
 
                   #    C l u s t e r   u s i n g   D B S C A N 
 
                 e m b e d d i n g s _ a r r a y   =   n p . a r r a y ( e m b e d d i n g s ) 
 
                 c l u s t e r i n g   =   D B S C A N ( e p s = 0 . 5 ,    m i n _ s a m p l e s = m i n _ s a m p l e s ) . f i t ( 
                                                                                                                                      
                                                                                                                                                              e m b e d d i n g s _ a r r a y ) 
 
 
 
                   #    G r o u p   m e m o r i e s   b y   c l u s t e r 
 
                 c l u s t e r s   =   d e f a u l t d i c t ( l i s t ) 
 
                 f o r   m e m o r y ,    l a b e l   i n   z i p ( m e m o r y _ l i s t ,    c l u s t e r i n g . l a b e l s _ ) :  
 
                         c l u s t e r s [ l a b e l ] . a p p e n d ( m e m o r y ) 
 
 
 
                 r e t u r n   d i c t ( c l u s t e r s ) 
 
 
 
         d e f   g e t _ m e m o r y _ c o u n t ( s e l f )   - >   i n t :  
 
                 " " " G e t   t o t a l   n u m b e r   o f   m e m o r i e s " " " 
 
                 i f   s e l f . i n d e x :  
 
                         r e t u r n   s e l f . i n d e x . n t o t a l 
 
                 r e t u r n   l e n ( s e l f . m e m o r i e s ) 
 
 
 
         d e f   g e t _ m e m o r i e s _ b y _ c h i l d ( s e l f ,    c h i l d _ i d :    s t r )   - >   L i s t [ M e m o r y ] :  
 
                 " " " G e t   a l l   m e m o r i e s   f o r   a   s p e c i f i c   c h i l d " " " 
 
                 r e t u r n   [ 
                                 
                                                         m e m o r y   f o r   m e m o r y   i n   s e l f . m e m o r i e s . v a l u e s ( ) 
                                 
                                                         i f   m e m o r y . c h i l d _ i d   = =   c h i l d _ i d 
                                 
                                                 ] 
 
 
 
         d e f   r e m o v e _ m e m o r y ( s e l f ,    m e m o r y _ i d :    s t r )   - >   b o o l :  
 
                 " " " R e m o v e   m e m o r y   f r o m   v e c t o r   s t o r e   ( s o f t   d e l e t i o n ) " " " 
 
                 f o r   i d x ,    m e m o r y   i n   s e l f . m e m o r i e s . i t e m s ( ) :  
 
                         i f   m e m o r y . i d   = =   m e m o r y _ i d :  
 
#    M a r k   a s   d e l e t e d   ( F A I S S   d o e s n ' t   s u p p o r t   r e m o v a l ) 
                                 
 
                                 m e m o r y . i m p o r t a n c e   =   M e m o r y I m p o r t a n c e . T R I V I A L 
 
                                 r e t u r n   T r u e 
 
                 r e t u r n   F a l s e 
 
 
 
         d e f   c l e a r _ c h i l d _ m e m o r i e s ( s e l f ,    c h i l d _ i d :    s t r )   - >   i n t :  
 
                 " " " C l e a r   a l l   m e m o r i e s   f o r   a   c h i l d " " " 
 
                 r e m o v e d _ c o u n t   =   0 
 
                 f o r   m e m o r y   i n   s e l f . m e m o r i e s . v a l u e s ( ) :  
 
                         i f   m e m o r y . c h i l d _ i d   = =   c h i l d _ i d :  
 
                                 m e m o r y . i m p o r t a n c e   =   M e m o r y I m p o r t a n c e . T R I V I A L 
 
                                 r e m o v e d _ c o u n t   + =   1 
 
                 r e t u r n   r e m o v e d _ c o u n t 
 
 
