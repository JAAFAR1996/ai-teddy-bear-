ÿþ  #  ! / u s r / b i n / e n v   p y t h o n 3 
 
 " " " 
 
 P a r e n t   N o t i f i c a t i o n   S e r v i c e   -   S i n g l e   R e s p o n s i b i l i t y 
 
 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
 
 E3$HD  AB7  9F  %13'D  'D%49'1'*  DDH'D/JF
 
 " " " 
 
 
 
 i m p o r t   l o g g i n g 
 
 f r o m   t y p i n g   i m p o r t   D i c t ,    O p t i o n a l 
 
 f r o m   d a t a c l a s s e s   i m p o r t   d a t a c l a s s 
 
 f r o m   d a t e t i m e   i m p o r t   d a t e t i m e 
 
 f r o m   e n u m   i m p o r t   E n u m 
 
 
 
 l o g g e r   =   l o g g i n g . g e t L o g g e r ( _ _ n a m e _ _ ) 
 
 
 
 c l a s s   N o t i f i c a t i o n T y p e ( E n u m ) :  
 
         " " " #FH'9  'D%49'1'*" " " 
 
         W E E K L Y _ R E P O R T   =   " w e e k l y _ r e p o r t " 
 
         U R G E N T _ C O N C E R N   =   " u r g e n t _ c o n c e r n " 
 
         M I L E S T O N E _ A C H I E V E D   =   " m i l e s t o n e _ a c h i e v e d " 
 
 
 
 c l a s s   N o t i f i c a t i o n P r i o r i t y ( E n u m ) :  
 
         " " " #HDHJ)  'D%49'1" " " 
 
         L O W   =   " l o w " 
 
         M E D I U M   =   " m e d i u m " 
 
         H I G H   =   " h i g h " 
 
         U R G E N T   =   " u r g e n t " 
 
 
 
 @ d a t a c l a s s 
 
 c l a s s   N o t i f i c a t i o n :  
 
         " " " %49'1  DDH'D/JF" " " 
 
         i d :    s t r 
 
         p a r e n t _ i d :    s t r 
 
         c h i l d _ i d :    s t r 
 
         t y p e :    N o t i f i c a t i o n T y p e 
 
         p r i o r i t y :    N o t i f i c a t i o n P r i o r i t y 
 
         t i t l e :    s t r 
 
         m e s s a g e :    s t r 
 
         d a t a :    O p t i o n a l [ D i c t ]   =   N o n e 
 
         c r e a t e d _ a t :    d a t e t i m e   =   N o n e 
 
 
 
 @ d a t a c l a s s 
 
 c l a s s   D e l i v e r y R e s u l t :  
 
         " " " F*J,)  %13'D  'D%49'1" " " 
 
         n o t i f i c a t i o n _ i d :    s t r 
 
         s u c c e s s :    b o o l 
 
         d e l i v e r y _ m e t h o d :    s t r 
 
         e r r o r _ m e s s a g e :    O p t i o n a l [ s t r ]   =   N o n e 
 
         d e l i v e r e d _ a t :    O p t i o n a l [ d a t e t i m e ]   =   N o n e 
 
 
 
 c l a s s   P a r e n t N o t i f i c a t i o n S e r v i c e :  
 
         " " " E3$HD  AB7  9F  %13'D  'D%49'1'*  DDH'D/JF" " " 
 
         
 
         d e f   _ _ i n i t _ _ ( s e l f ,    e m a i l _ s e r v i c e = N o n e ,    p u s h _ s e r v i c e = N o n e ) :  
 
                 s e l f . e m a i l _ s e r v i c e   =   e m a i l _ s e r v i c e 
 
                 s e l f . p u s h _ s e r v i c e   =   p u s h _ s e r v i c e 
 
                 
 
         a s y n c   d e f   n o t i f y ( s e l f ,    p a r e n t _ i d :    s t r ,    n o t i f i c a t i o n :    N o t i f i c a t i o n )   - >   D e l i v e r y R e s u l t :  
 
                 " " " 
 
                 %13'D  %49'1  DDH'D/  -   'DE3$HDJ)  'DH-J/)  DG0'  'DCD'3
 
                 " " " 
 
                 t r y :  
 
                         i f   n o t   s e l f . _ v a l i d a t e _ n o t i f i c a t i o n ( n o t i f i c a t i o n ) :  
 
                                 r e t u r n   D e l i v e r y R e s u l t ( 
 
                                         n o t i f i c a t i o n _ i d = n o t i f i c a t i o n . i d ,  
 
                                         s u c c e s s = F a l s e ,  
 
                                         d e l i v e r y _ m e t h o d = " n o n e " ,  
 
                                         e r r o r _ m e s s a g e = " I n v a l i d   n o t i f i c a t i o n   d a t a " 
 
                                 ) 
 
                         
 
                           #    *-/J/  71JB)  'D%13'D
 
                         d e l i v e r y _ m e t h o d   =   s e l f . _ g e t _ d e l i v e r y _ m e t h o d ( n o t i f i c a t i o n . p r i o r i t y ) 
 
                         
 
                           #    %13'D  'D%49'1
 
                         r e s u l t   =   a w a i t   s e l f . _ s e n d _ n o t i f i c a t i o n ( n o t i f i c a t i o n ,    d e l i v e r y _ m e t h o d ) 
 
                         
 
                         l o g g e r . i n f o ( f " N o t i f i c a t i o n   { n o t i f i c a t i o n . i d }   p r o c e s s e d " ) 
 
                         r e t u r n   r e s u l t 
 
                         
 
                 e x c e p t   E x c e p t i o n   a s   e :  
 
                         l o g g e r . e r r o r ( f " N o t i f i c a t i o n   e r r o r :   { e } " ) 
 
                         r e t u r n   D e l i v e r y R e s u l t ( 
 
                                 n o t i f i c a t i o n _ i d = n o t i f i c a t i o n . i d ,  
 
                                 s u c c e s s = F a l s e ,  
 
                                 d e l i v e r y _ m e t h o d = " n o n e " ,  
 
                                 e r r o r _ m e s s a g e = s t r ( e ) 
 
                         ) 
 
         
 
         d e f   _ v a l i d a t e _ n o t i f i c a t i o n ( s e l f ,    n o t i f i c a t i o n :    N o t i f i c a t i o n )   - >   b o o l :  
 
                 " " " 'D*-BB  EF  5-)  (J'F'*  'D%49'1" " " 
 
                 r e t u r n   ( n o t i f i c a t i o n . p a r e n t _ i d   a n d   n o t i f i c a t i o n . c h i l d _ i d   a n d   
 
                                 n o t i f i c a t i o n . t i t l e   a n d   n o t i f i c a t i o n . m e s s a g e ) 
 
         
 
         d e f   _ g e t _ d e l i v e r y _ m e t h o d ( s e l f ,    p r i o r i t y :    N o t i f i c a t i o n P r i o r i t y )   - >   s t r :  
 
                 " " " *-/J/  71JB)  'D%13'D" " " 
 
                 i f   p r i o r i t y   = =   N o t i f i c a t i o n P r i o r i t y . U R G E N T   a n d   s e l f . p u s h _ s e r v i c e :  
 
                         r e t u r n   ' p u s h ' 
 
                 e l i f   s e l f . e m a i l _ s e r v i c e :  
 
                         r e t u r n   ' e m a i l ' 
 
                 r e t u r n   ' n o n e ' 
 
         
 
         a s y n c   d e f   _ s e n d _ n o t i f i c a t i o n ( s e l f ,    n o t i f i c a t i o n :    N o t i f i c a t i o n ,    m e t h o d :    s t r )   - >   D e l i v e r y R e s u l t :  
 
                 " " " %13'D  'D%49'1" " " 
 
                 t r y :  
 
                         i f   m e t h o d   = =   ' p u s h ' :  
 
                                 r e t u r n   a w a i t   s e l f . _ s e n d _ p u s h ( n o t i f i c a t i o n ) 
 
                         e l i f   m e t h o d   = =   ' e m a i l ' :  
 
                                 r e t u r n   a w a i t   s e l f . _ s e n d _ e m a i l ( n o t i f i c a t i o n ) 
 
                         e l s e :  
 
                                 r e t u r n   D e l i v e r y R e s u l t ( 
 
                                         n o t i f i c a t i o n _ i d = n o t i f i c a t i o n . i d ,  
 
                                         s u c c e s s = F a l s e ,  
 
                                         d e l i v e r y _ m e t h o d = m e t h o d ,  
 
                                         e r r o r _ m e s s a g e = " M e t h o d   n o t   a v a i l a b l e " 
 
                                 ) 
 
                 e x c e p t   E x c e p t i o n   a s   e :  
 
                         r e t u r n   D e l i v e r y R e s u l t ( 
 
                                 n o t i f i c a t i o n _ i d = n o t i f i c a t i o n . i d ,  
 
                                 s u c c e s s = F a l s e ,  
 
                                 d e l i v e r y _ m e t h o d = m e t h o d ,  
 
                                 e r r o r _ m e s s a g e = s t r ( e ) 
 
                         ) 
 
         
 
         a s y n c   d e f   _ s e n d _ p u s h ( s e l f ,    n o t i f i c a t i o n :    N o t i f i c a t i o n )   - >   D e l i v e r y R e s u l t :  
 
                 " " " %13'D  P u s h   n o t i f i c a t i o n " " " 
 
                 l o g g e r . i n f o ( f " P u s h   s e n t :   { n o t i f i c a t i o n . t i t l e } " ) 
 
                 r e t u r n   D e l i v e r y R e s u l t ( 
 
                         n o t i f i c a t i o n _ i d = n o t i f i c a t i o n . i d ,  
 
                         s u c c e s s = T r u e ,  
 
                         d e l i v e r y _ m e t h o d = ' p u s h ' ,  
 
                         d e l i v e r e d _ a t = d a t e t i m e . n o w ( ) 
 
                 ) 
 
         
 
         a s y n c   d e f   _ s e n d _ e m a i l ( s e l f ,    n o t i f i c a t i o n :    N o t i f i c a t i o n )   - >   D e l i v e r y R e s u l t :  
 
                 " " " %13'D  E m a i l   n o t i f i c a t i o n " " " 
 
                 l o g g e r . i n f o ( f " E m a i l   s e n t :   { n o t i f i c a t i o n . t i t l e } " ) 
 
                 r e t u r n   D e l i v e r y R e s u l t ( 
 
                         n o t i f i c a t i o n _ i d = n o t i f i c a t i o n . i d ,  
 
                         s u c c e s s = T r u e ,  
 
                         d e l i v e r y _ m e t h o d = ' e m a i l ' ,  
 
                         d e l i v e r e d _ a t = d a t e t i m e . n o w ( ) 
 
                 ) 
 
 
