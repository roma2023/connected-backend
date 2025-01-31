import React from 'react';
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Toolbar, Typography } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import CreateIcon from '@mui/icons-material/Create';
import LibraryMusicIcon from '@mui/icons-material/LibraryMusic';
import MenuBookIcon from '@mui/icons-material/MenuBook';

const drawerWidth = 240;

const SideNav = ({ onSelect }) => {
  const menuItems = [
    { text: 'Home', icon: <HomeIcon />, onClick: () => onSelect('home') },
    { text: 'Generate with AI', icon: <CreateIcon />, onClick: () => onSelect('generate') },
    { text: 'Your Podcasts', icon: <LibraryMusicIcon />, onClick: () => onSelect('podcasts') },
    { text: 'Your Study Guides', icon: <MenuBookIcon />, onClick: () => onSelect('study_guides') },
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
      }}
    >
      <Toolbar>
        <Typography variant="h6" noWrap>
          AI Inference
        </Typography>
      </Toolbar>
      <List>
        {menuItems.map((item, index) => (
          <ListItem button key={index} onClick={item.onClick}>
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};

export default SideNav;